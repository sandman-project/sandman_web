"""Tests the reports pages."""

import flask
import flask.testing
import pytest
import whenever

import sandman_web.reports.reports as reports


def test_reports(client: flask.testing.FlaskClient) -> None:
    """Test the reports page."""
    response = client.get("/reports/")
    assert response.status_code == 200
    assert b"/reports/2024/12/8/report" in response.data


@pytest.mark.parametrize(
    ("url", "status_code", "message"),
    (
        ("/reports/2024/12/8/report", 200, b"2024-12-08"),
        ("/reports/2024/12/9/report", 404, b""),
    ),
)
def test_report(
    client: flask.testing.FlaskClient, url: str, status_code: int, message: str
) -> None:
    """Test the individual report page."""
    response = client.get(url)
    assert response.status_code == status_code
    assert message in response.data


_default_report_event_when = None
_default_report_event_info = {}


def _check_default_report_event(event: reports.ReportEvent) -> None:
    """Check that the report event has default values."""
    assert event.when == _default_report_event_when
    assert event.info == _default_report_event_info
    assert event.is_valid() == False


def test_report_event_initialization() -> None:
    """Test initializing report events."""
    event = reports.ReportEvent()
    _check_default_report_event(event)

    with pytest.raises(TypeError):
        event.when = ""
    _check_default_report_event(event)

    intended_time = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=29,
        hour=18,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    event.when = intended_time
    assert event.when == intended_time
    assert event.info == _default_report_event_info
    assert event.is_valid() == False

    with pytest.raises(TypeError):
        event.info = 1
    event.when = intended_time
    assert event.when == intended_time
    assert event.info == _default_report_event_info
    assert event.is_valid() == False

    intended_info: reports.ReportEventInfo = {
        "type": "control",
        "control": "test_control",
        "action": "up",
        "source": "voice",
    }
    event.info = intended_info
    assert event.when == intended_time
    assert event.info == intended_info
    assert event.is_valid() == True


_default_report_version = -1
_default_report_start = None


def _check_default_report(report: reports.Report) -> None:
    """Check that the report has default values."""
    assert report.version == _default_report_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False


def test_report_initialization() -> None:
    """Test initializing reports."""
    report = reports.Report()
    _check_default_report(report)

    with pytest.raises(TypeError):
        report.version = ""
    _check_default_report(report)

    with pytest.raises(ValueError):
        report.version = -2
    _check_default_report(report)

    intended_version = 3

    report.version = intended_version
    assert report.version == intended_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False

    with pytest.raises(TypeError):
        report.start = ""
    assert report.version == intended_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False

    start_time = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=29,
        hour=17,
        minute=0,
        second=0,
        tz="America/Chicago",
    )
    report.start = start_time
    assert report.version == intended_version
    assert report.start == start_time
    assert len(report.events) == 0
    assert report.is_valid() == True

    # Add some events.

    first_time = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=29,
        hour=18,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    first_info: reports.ReportEventInfo = {
        "type": "control",
        "control": "test_control",
        "action": "up",
        "source": "voice",
    }
    first_event = reports.ReportEvent()
    first_event.when = first_time
    first_event.info = first_info
    assert first_event.is_valid() == True

    report.append_event(first_event)
    assert report.version == intended_version
    assert report.start == start_time
    assert len(report.events) == 1
    if len(report.events) > 0:
        assert report.events[0] == first_event
    assert report.is_valid() == True

    second_time = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=29,
        hour=19,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    second_info: reports.ReportEventInfo = {
        "type": "routine",
        "routine": "wake",
        "action": "up",
    }
    second_event = reports.ReportEvent()
    second_event.when = second_time
    second_event.info = second_info
    assert second_event.is_valid() == True

    report.append_event(second_event)
    assert report.version == intended_version
    assert report.start == start_time
    assert len(report.events) == 2
    if len(report.events) > 1:
        assert report.events[0] == first_event
        assert report.events[1] == second_event
    assert report.is_valid() == True


def test_report_loading() -> None:
    """Test loading report files."""
    path: str = "tests/data/reports/"

    with pytest.raises(FileNotFoundError):
        report = reports.Report.parse_from_file(path + "a")

    # Empty files cannot be parsed.
    report = reports.Report.parse_from_file(path + "report_test_empty.rpt")
    _check_default_report(report)

    # Must have a valid header.
    report = reports.Report.parse_from_file(
        path + "report_test_invalid_header.rpt"
    )
    _check_default_report(report)

    report = reports.Report.parse_from_file(
        path + "report_test_missing_version.rpt"
    )
    _check_default_report(report)

    report = reports.Report.parse_from_file(
        path + "report_test_type_version.rpt"
    )
    _check_default_report(report)

    report = reports.Report.parse_from_file(
        path + "report_test_invalid_version.rpt"
    )
    _check_default_report(report)

    # Beyond this point we have valid versions.
    expected_version = 4

    report = reports.Report.parse_from_file(
        path + "report_test_missing_start.rpt"
    )
    assert report.version == expected_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False

    report = reports.Report.parse_from_file(
        path + "report_test_type_start.rpt"
    )
    assert report.version == expected_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False

    report = reports.Report.parse_from_file(
        path + "report_test_invalid_start.rpt"
    )
    assert report.version == expected_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False
