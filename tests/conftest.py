import pytest

import flask
import flask.testing

import sandman_web

@pytest.fixture
def app() -> flask.Flask:

   app = sandman_web.create_app({"TESTING": True})

   yield app

@pytest.fixture
def client(app) -> flask.testing.FlaskClient:
   return app.test_client()