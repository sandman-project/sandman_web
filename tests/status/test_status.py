"""Tests the status page."""

import flask
import flask.testing


def test_status(client: flask.testing.FlaskClient) -> None:
    """Test the status page."""
    assert client.get("/status").status_code == 200
