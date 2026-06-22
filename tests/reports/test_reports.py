"""Tests the reports pages."""

import flask
import flask.testing
import pytest


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
