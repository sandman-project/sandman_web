"""Implements the status webpage."""

import enum

import flask
import requests


class _HealthType(enum.Enum):
    RUNNING = 1
    NOT_RUNNING = 2
    NOT_FOUND = 3


def _check_sandman_health() -> _HealthType:
    """Check the health of Sandman."""
    return _HealthType.NOT_RUNNING


def _check_rhasspy_health() -> _HealthType:
    """Check the health of Rhasspy."""
    # Get the Rhasspy web response.
    try:
        web_response = requests.get("http://localhost:12101")

    except Exception:
        return _HealthType.NOT_RUNNING

    web_status = web_response.status_code

    # Check that the Rhasspy web response is OK.
    if web_status == 200:
        return _HealthType.RUNNING

    return _HealthType.NOT_RUNNING


def is_healthy() -> bool:
    """Return whether the status is healthy overall."""
    sandman_health = _check_sandman_health()
    rhasspy_health = _check_rhasspy_health()

    if (
        sandman_health == _HealthType.RUNNING
        and rhasspy_health == _HealthType.RUNNING
    ):
        return True

    return False


status_bp = flask.Blueprint("status", __name__, template_folder="templates")


@status_bp.route("/status")
def status_home() -> str:
    """Implement the route for the status page."""
    # Perform the Sandman related health checks.
    sandman_health = _check_sandman_health()
    rhasspy_health = _check_rhasspy_health()

    # Check that Sandman is in good health.
    if sandman_health == _HealthType.RUNNING:
        sandman_status = "Sandman is running. ✔️"
    else:
        sandman_status = "Sandman is not running. ❌"

    # Check that Rhasspy is in good health.
    if rhasspy_health == _HealthType.RUNNING:
        rhasspy_status = "Rhasspy is running. ✔️"
    else:
        rhasspy_status = "Rhasspy is not running. ❌"
        if rhasspy_health == _HealthType.NOT_FOUND:
            rhasspy_status += "The Rhasspy container may not exist."

    return flask.render_template(
        "status.html",
        sandman_status=sandman_status,
        rhasspy_status=rhasspy_status,
    )
