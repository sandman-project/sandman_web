"""Implements the reports list and individual reports webpages."""

import datetime
import json
import logging
import os
import typing
from operator import itemgetter

import flask
import whenever
from werkzeug.exceptions import abort

_logger = logging.getLogger("sandman.routines")

_report_prefix = "sandman"
_report_extension = ".rpt"

# The date and time format for report events.
_report_date_time_format = "%Y/%m/%d %H:%M:%S %Z"


type ReportEventInfo = typing.Mapping[
    str, typing.Mapping[str, int | str] | int | str
]


class ReportEvent:
    """An event for a report file."""

    def __init__(self) -> None:
        """Initialize the report event."""
        self.__when: whenever.ZonedDateTime | None = None
        self.__info: ReportEventInfo = {}

    @property
    def when(self) -> whenever.ZonedDateTime | None:
        """Get the when."""
        return self.__when

    @when.setter
    def when(self, when: whenever.ZonedDateTime) -> None:
        """Set the when."""
        if isinstance(when, whenever.ZonedDateTime) == False:
            raise TypeError("When must be a zoned date/time.")

        self.__when = when

    @property
    def info(self) -> ReportEventInfo:
        """Get the info."""
        return self.__info

    @info.setter
    def info(self, info: ReportEventInfo) -> None:
        """Set the info."""
        if isinstance(info, dict) == False:
            raise TypeError("Info must be a ReportEventInfo.")

        # This will be more robust if the info is a concrete type.

        self.__info = info

    def is_valid(self) -> bool:
        """Check whether this is a valid report event."""
        if self.__when is None:
            return False

        # This will be a lot more robust if the info becomes a concrete class.
        if self.__info == {}:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this event and another have equal values."""
        if not isinstance(other, ReportEvent):
            return NotImplemented

        return (self.__when == other.__when) and (self.__info == other.__info)

    @classmethod
    def parse_from_string(
        cls, event_string: str, filename: str
    ) -> typing.Self:
        """Parse the event from a (JSON) string."""
        event = cls()

        try:
            event_json = json.loads(event_string)

        except json.JSONDecodeError:
            _logger.warning(
                "JSON error decoding event for report file '%s'.",
                filename,
            )
            return event

        try:
            event.when = whenever.ZonedDateTime.parse_iso(event_json["when"])

        except KeyError:
            _logger.warning(
                "Missing 'when' key in event in report file '%s'.",
                filename,
            )
            return event

        except (TypeError, ValueError):
            _logger.warning(
                "Invalid when '%s' in event in report file '%s'.",
                str(event_json["when"]),
                filename,
            )
            return event

        return event


class Report:
    """All of the information from a report file."""

    def __init__(self) -> None:
        """Initialize the report."""
        self.__version = -1
        self.__start: whenever.ZonedDateTime | None = None
        self.__events: list[ReportEvent] = []

    @property
    def version(self) -> int:
        """Get the version."""
        return self.__version

    @version.setter
    def version(self, version: int) -> None:
        """Set the version."""
        if isinstance(version, int) == False:
            raise TypeError("Version must be an integer.")

        if version < 0:
            raise ValueError("Cannot set a negative version.")

        self.__version = version

    @property
    def start(self) -> whenever.ZonedDateTime | None:
        """Get the start."""
        return self.__start

    @start.setter
    def start(self, start: whenever.ZonedDateTime) -> None:
        """Set the start."""
        if isinstance(start, whenever.ZonedDateTime) == False:
            raise TypeError("Start must be a zoned date/time.")

        self.__start = start

    @property
    def events(self) -> list[ReportEvent]:
        """Get the events."""
        return self.__events

    def append_event(self, event: ReportEvent) -> None:
        """Add an event to the end."""
        self.__events.append(event)

    def is_valid(self) -> bool:
        """Check whether this is a valid report."""
        if self.__version < 0:
            return False

        if self.__start is None:
            return False

        return True

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse a report from a file."""
        report = cls()

        try:
            with open(filename) as file:
                report_lines = file.readlines()

        except FileNotFoundError as error:
            _logger.error("Could not find report file '%s'.", filename)
            raise error

        num_lines = len(report_lines)

        if num_lines == 0:
            _logger.warning("Report file '%s' is empty.", filename)
            return report

        # The first line is expected to be the header.
        try:
            header_json = json.loads(report_lines[0])

        except json.JSONDecodeError:
            _logger.error(
                "JSON error decoding header for report file '%s'.",
                filename,
            )
            return report

        try:
            report.version = header_json["version"]

        except KeyError:
            _logger.error("Missing version in report file '%s'.", filename)
            return report

        except (TypeError, ValueError):
            _logger.error(
                "Invalid version '%s' in report file '%s'.",
                str(header_json["version"]),
                filename,
            )
            return report

        # Don't support loading reports older than version 4.
        if report.version < 4:
            return report

        try:
            report.start = whenever.ZonedDateTime.parse_iso(
                header_json["start"]
            )

        except KeyError:
            _logger.error("Missing start in report file '%s'.", filename)
            return report

        except (TypeError, ValueError):
            _logger.error(
                "Invalid start '%s' in report file '%s'.",
                str(header_json["start"]),
                filename,
            )
            return report

        # Load the events.
        for line_index in range(1, num_lines):
            event = ReportEvent.parse_from_string(
                report_lines[line_index], filename
            )

            if event.is_valid() == True:
                report.append_event(event)

        return report


def _get_reports_path() -> str:
    return flask.current_app.config["BASE_DIR"] + "/reports"


blueprint = flask.Blueprint(
    "reports",
    __name__,
    url_prefix="/reports",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/")
def index() -> str:
    """Implement the page listing all of the reports."""
    reports_path = _get_reports_path()

    # Build a list of all the reports.
    reports = []

    for path in os.listdir(reports_path):
        base_name, extension = os.path.splitext(path)

        if extension != _report_extension:
            continue

        # We expect all of the reports to start with the same prefix, so
        # ignore any that don't have it.
        if base_name.startswith(_report_prefix) == False:
            continue

        date_string = base_name[len(_report_prefix) :]

        # Try to convert the name to a date.
        date_format = "%Y-%m-%d"

        try:
            date = datetime.datetime.strptime(date_string, date_format)

        except ValueError:
            continue

        # Add a dictionary containing the date.
        reports.append(
            {"year": date.year, "month": date.month, "day": date.day}
        )

    # Sort them in descending order.
    sorted_reports = sorted(
        reports, key=itemgetter("year", "month", "day"), reverse=True
    )

    return flask.render_template("reports.html", reports=sorted_reports)


def _update_report_event_from_version_3(event: dict[any]) -> None:
    # Handle the schedule -> routine rename on on old data.
    if event["type"] == "schedule":
        event["type"] = "routine"

    if event["type"] == "control" and event["source"] == "schedule":
        event["source"] = "routine"


def _make_report_event_from_version_2(event: str) -> dict[any]:
    # Convert the event into the most likely sort of control event.
    control_action_parts = event.split(": ")
    control_name = control_action_parts[0]

    control_action = "stop"
    if control_action_parts[1] == "moving up":
        control_action = "move up"
    elif control_action_parts[1] == "moving down":
        control_action = "move down"

    converted_event = {
        "type": "control",
        "control": control_name,
        "action": control_action,
        "source": "command",
    }

    return converted_event


def _parse_report_file(filename: str) -> tuple[int, list[any]]:
    """Parse a report file.

    Returns a tuple containing the version as the first element (or None if
    there was an error). The second element of the tuple is a list of tuples.
    These list elements correspond to events from the report, where the first
    element is the date and time, and the second is the event information.
    """
    version = None
    infos = []

    try:
        with open(filename, encoding="utf-8") as report_file:
            # Process every line of the file.
            for line_index, line in enumerate(report_file):
                # Try to convert the line to JSON.
                try:
                    line_json = json.loads(line)

                except json.JSONDecodeError:
                    continue

                # The first line should be the header information.
                if line_index == 0:
                    version = line_json.get("version")

                    if version is None:
                        break

                else:
                    # Get the date and time and convert it to an object.
                    line_date_time = line_json.get("when")

                    if line_date_time is None:
                        continue

                    try:
                        info_date_time = whenever.ZonedDateTime.parse_iso()

                    except ValueError:
                        continue

                    line_event = line_json.get("event")

                    if line_event is None:
                        line_event = "None"

                    if version == 3:
                        _update_report_event_from_version_3(line_event)

                    elif version == 2:
                        line_event = _make_report_event_from_version_2(
                            line_event
                        )

                    infos.append((info_date_time, line_event))

    except OSError:
        return (version, infos)

    return (version, infos)


@blueprint.route("/<int:year>/<int:month>/<int:day>/report")
def report(year: int, month: int, day: int) -> str:
    """Implement the page for a specific report."""
    reports_path = _get_reports_path()

    report_name = f"{year:04d}-{month:02d}-{day:02d}"
    report_filename = (
        reports_path + "/" + _report_prefix + report_name + _report_extension
    )

    # Try to generate a report start time to fall back on if we don't get one
    # from the file.
    date_format = "%Y-%m-%d"

    try:
        report_end_date = datetime.datetime.strptime(report_name, date_format)

    except ValueError:
        abort(404, "Oops!")

    # The start date is one day before.
    report_start_date_time = report_end_date + datetime.timedelta(
        days=-1, hours=17
    )

    # Attempt to parse the data in the file.
    report_version, report_infos = _parse_report_file(report_filename)

    if report_version is None:
        abort(404, "Oops!")

    # Now that we have pulled data out of the file, do some processing to
    # convert it to what we need for display. Part of that will be converting
    # to dictionaries but also calculating the offset from the start time.
    event_infos = []

    for date_time, event in report_infos:
        # Figure out how many seconds from the start this event is.
        seconds_from_start = int(
            (date_time - report_start_date_time).total_seconds()
        )

        event_info = {
            "year": date_time.year,
            "month": date_time.month,
            "day": date_time.day,
            "hour": date_time.hour,
            "minute": date_time.minute,
            "second": date_time.second,
            "secondsFromStart": seconds_from_start,
            "event": event,
        }

        event_infos.append(event_info)

    report_start_date_string = report_start_date_time.strftime("%Y-%m-%d")

    # Either generate these from the start time or based on the actual data
    # set in the future.
    start_hour = 17

    return flask.render_template(
        "report.html",
        start_date_string=report_start_date_string,
        end_date_string=report_name,
        start_hour=start_hour,
        event_infos=event_infos,
    )
