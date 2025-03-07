"""Home for test fixtures, etc."""

import flask
import flask.testing
import pytest

import sandman_web


@pytest.fixture
def app() -> flask.Flask:
    """Return a test app."""
    app = sandman_web.create_app({"TESTING": True})

    yield app


@pytest.fixture
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    """Return a test client."""
    return app.test_client()
