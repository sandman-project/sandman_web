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
    assert b"/reports/2026/3/2/report" in response.data


@pytest.mark.parametrize(
    ("url", "status_code", "message"),
    (
        ("/reports/2024/12/8/report", 404, b""),
        ("/reports/2024/12/9/report", 404, b""),
        ("/reports/2026/3/2/report", 200, b"2026-03-02"),
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


def _check_expected_report_events(
    events: list[reports.ReportEvent],
    expected_events: list[reports.ReportEvent],
) -> None:
    """Check whether report events match expected values."""
    num_events = len(events)
    num_expected_events = len(expected_events)
    assert num_events == num_expected_events

    if num_events != num_expected_events:
        return

    for index in range(num_events):
        assert events[index] == expected_events[index]


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

    expected_version = 3

    report.version = expected_version
    assert report.version == expected_version
    assert report.start == _default_report_start
    assert len(report.events) == 0
    assert report.is_valid() == False

    with pytest.raises(TypeError):
        report.start = ""
    assert report.version == expected_version
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
    assert report.version == expected_version
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
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [first_event])
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
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [first_event, second_event])
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

    # Now we are testing events.
    start_time = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=2,
        hour=17,
        minute=0,
        second=0,
        tz="America/Chicago",
    )

    time0 = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=2,
        hour=23,
        minute=44,
        second=49,
        tz="America/Chicago",
    )

    time1 = whenever.ZonedDateTime(
        year=2026,
        month=3,
        day=2,
        hour=23,
        minute=44,
        second=50,
        tz="America/Chicago",
    )

    expected_event0 = reports.ReportEvent()
    expected_event0.when = time0
    expected_event0.info = {
        "type": "control",
        "control": "back",
        "action": "up",
        "source": "voice",
    }
    assert expected_event0.is_valid() == True

    expected_event1 = reports.ReportEvent()
    expected_event1.when = time1
    expected_event1.info = {
        "type": "control",
        "control": "back",
        "action": "down",
        "source": "voice",
    }
    assert expected_event1.is_valid() == True

    expected_events = [expected_event0, expected_event1]

    report = reports.Report.parse_from_file(
        path + "report_test_event_invalid.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_missing_when.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_type_when.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_invalid_when.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_missing_info.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_type_info.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_event_invalid_info.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, [expected_event1])
    assert report.is_valid() == True

    report = reports.Report.parse_from_file(
        path + "report_test_valid_events.rpt"
    )
    assert report.version == expected_version
    assert report.start == start_time
    _check_expected_report_events(report.events, expected_events)
    assert report.is_valid() == True
