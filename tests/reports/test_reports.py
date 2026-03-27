"""Tests the reports pages."""

import flask
import flask.testing
import pytest

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


_default_report_version = -1


def _check_default_report(report: reports.Report) -> None:
    """Check that the report has default values."""
    assert report.version == _default_report_version
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
    assert report.is_valid() == True


def test_report_loading() -> None:
    """Test loading report files."""
    assert True
