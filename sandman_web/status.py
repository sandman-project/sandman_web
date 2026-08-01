"""Implements the status webpage."""

import enum
import os

import flask
import requests


class _HealthType(enum.Enum):
    HEALTHY = 1
    NOT_HEALTHY = 2


def _check_sandman_health() -> _HealthType:
    """Check the health of Sandman."""
    return _HealthType.NOT_HEALTHY


def _check_rhasspy_health() -> _HealthType:
    """Check the health of Rhasspy."""
    hostname = os.environ.get("RHASSPY_HOSTNAME", "localhost")
    address = f"http://{hostname}:12101"

    # Get the Rhasspy web response.
    try:
        web_response = requests.get(address)

    except Exception:
        return _HealthType.NOT_HEALTHY

    web_status = web_response.status_code

    # Check that the Rhasspy web response is OK.
    if web_status == 200:
        return _HealthType.HEALTHY

    return _HealthType.NOT_HEALTHY


def is_healthy() -> bool:
    """Return whether the status is healthy overall."""
    _sandman_health = _check_sandman_health()
    rhasspy_health = _check_rhasspy_health()

    # For now we don't include the Sandman health check, because it needs to
    # be reimplemented.
    if rhasspy_health == _HealthType.HEALTHY:
        return True

    return False


status_bp = flask.Blueprint("status", __name__, template_folder="templates")


@status_bp.route("/status")
def status_home() -> str:
    """Implement the route for the status page."""
    # Perform the Sandman related health checks.
    _sandman_health = _check_sandman_health()
    rhasspy_health = _check_rhasspy_health()

    # Check that Sandman is in good health.
    sandman_status = "Sandman health is unknown."

    # Check that Rhasspy is in good health.
    if rhasspy_health == _HealthType.HEALTHY:
        rhasspy_status = "Rhasspy is healthy. ✔️"
    else:
        rhasspy_status = "Rhasspy is not healthy. ❌"

    return flask.render_template(
        "status.html",
        sandman_status=sandman_status,
        rhasspy_status=rhasspy_status,
    )
