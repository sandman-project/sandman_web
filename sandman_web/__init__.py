"""The web interface for interacting with Sandman."""

import logging
import logging.handlers
import os
import pathlib
import typing

import flask
import werkzeug


def _setup_logging(base_dir: str) -> None:
    """Set up logging."""
    logger = logging.getLogger("sandman")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s: %(message)s"
    )

    file_handler = logging.handlers.RotatingFileHandler(
        base_dir + "sandman_web.log", backupCount=10, maxBytes=1000000
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def create_app(
    test_config: dict[typing.Any, typing.Any] | None = None,
) -> flask.Flask:
    """Create and configure the app.

    test_config - Which testing configuration to use, if any.
    """
    app = flask.Flask(__name__, instance_relative_config=True)

    # Get the base directory for the data files.
    base_dir = str(pathlib.Path.home()) + "/.sandman"

    base_path = pathlib.Path(base_dir)

    # If the base directory doesn't exist, try to create it.
    base_dir_exists = base_path.exists()

    if base_dir_exists == False:
        try:
            base_path.mkdir()

        except Exception:
            print(f"Failed to create base directory '{base_dir}'")

    _setup_logging(base_dir + "/")

    app.config.from_mapping(
        SECRET_KEY="dev",
        BASE_DIR=base_dir,
    )

    if test_config is None:
        # Load the instance config when not testing, if it exists.
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Otherwise use the test config.
        app.config.from_mapping(test_config)

    # Make sure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Sandman Reports Home Page
    @app.route("/")
    def home() -> str:
        return reports.index()

    # A path to redirect to the rhasspy admin home page.
    @app.route("/rhasspy")
    def rhasspy() -> werkzeug.wrappers.response.Response:
        server_ip = flask.request.host.split(":")[0]
        return flask.redirect("http://" + server_ip + ":12101")

    # Register blueprints.
    from . import reports

    app.register_blueprint(reports.blueprint)

    from . import status

    app.register_blueprint(status.status_bp)

    # Create global status variable.
    @app.context_processor
    def status_processor() -> dict[typing.Any, typing.Any]:
        if status.is_healthy() == True:
            health_issue = False
        else:
            health_issue = True
        return dict(health_issue=health_issue)

    return app
