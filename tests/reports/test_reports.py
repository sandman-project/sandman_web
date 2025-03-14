"""Tests the reports pages."""

import flask
import flask.testing


def test_reports(client: flask.testing.FlaskClient) -> None:
    """Test the reports pages."""
    assert client.get("/reports/").status_code == 200
