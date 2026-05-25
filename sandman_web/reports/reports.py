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
        if info == {}:
            raise ValueError("Info must not be an empty dictionary.")

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

        try:
            info = event_json["info"]

        except KeyError:
            _logger.warning(
                "Missing 'info' key in event in report file '%s'.",
                filename,
            )

        else:
            if isinstance(info, dict) == True:
                try:
                    event.info = dict(info)

                except ValueError:
                    _logger.warning(
                        "Invalid info '%s' in event in report file '%s'.",
                        str(info),
                        filename,
                    )

            else:
                _logger.warning(
                    "Invalid info '%s' in event in report file '%s'.",
                    str(info),
                    filename,
                )

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


@blueprint.route("/<int:year>/<int:month>/<int:day>/report")
def report(year: int, month: int, day: int) -> str:
    """Implement the page for a specific report."""
    reports_path = _get_reports_path()

    report_name = f"{year:04d}-{month:02d}-{day:02d}"
    report_filename = (
        reports_path + "/" + _report_prefix + report_name + _report_extension
    )

    # Attempt to parse the data in the file.
    try:
        loaded_report = Report.parse_from_file(report_filename)

    except FileNotFoundError:
        abort(404, "Report not found.")

    if loaded_report.is_valid() == False:
        abort(404, "Report invalid.")

    report_start = loaded_report.start

    # Now that we have pulled data out of the file, do some processing to
    # convert it to what we need for display. Part of that will be converting
    # to dictionaries but also calculating the offset from the start time.
    event_infos = []

    for event in loaded_report.events:
        if event.is_valid() == False:
            continue

        event_time = event.when

        # Figure out how many seconds from the start this event is.
        since_start = event_time - report_start
        seconds_from_start = int(since_start.in_seconds())

        event_info = {
            "year": event_time.year,
            "month": event_time.month,
            "day": event_time.day,
            "hour": event_time.hour,
            "minute": event_time.minute,
            "second": event_time.second,
            "secondsFromStart": seconds_from_start,
            "info": event.info,
        }

        event_infos.append(event_info)

    report_start_date_string = (
        f"{report_start.year:04d}-"
        + f"{report_start.month:02d}-"
        + f"{report_start.day:02d}"
    )

    start_hour = report_start.hour

    return flask.render_template(
        "report.html",
        start_date_string=report_start_date_string,
        end_date_string=report_name,
        start_hour=start_hour,
        event_infos=event_infos,
    )
