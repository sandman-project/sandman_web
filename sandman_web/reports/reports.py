"""Implements the reports list and individual reports webpages."""

import logging
import os
from operator import itemgetter

import flask
import sandman_core.reports as reports
from werkzeug.exceptions import abort

_logger = logging.getLogger("sandman.reports")

_report_prefix = "sandman"
_report_extension = ".rpt"


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

        # Try to convert the name to a date. Expected format: YYYY-MM-DD
        date_elements = date_string.split("-")

        if len(date_elements) < 3:
            continue

        try:
            year = int(date_elements[0])

        except ValueError:
            continue

        try:
            month = int(date_elements[1])

        except ValueError:
            continue

        try:
            day = int(date_elements[2])

        except ValueError:
            continue

        # Add a dictionary containing the date.
        reports.append({"year": year, "month": month, "day": day})

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
        loaded_report = reports.Report.parse_from_file(report_filename)

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
        seconds_from_start = int(since_start.total("seconds"))

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

    report_end = report_start.add(hours=24)

    report_start_date_string = (
        f"{report_start.year:04d}-"
        + f"{report_start.month:02d}-"
        + f"{report_start.day:02d}"
    )

    report_end_date_string = (
        f"{report_end.year:04d}-"
        + f"{report_end.month:02d}-"
        + f"{report_end.day:02d}"
    )

    start_hour = report_start.hour

    return flask.render_template(
        "report.html",
        start_date_string=report_start_date_string,
        end_date_string=report_end_date_string,
        start_hour=start_hour,
        event_infos=event_infos,
    )
