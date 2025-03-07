[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sandman-project/sandman_web/main.svg)](https://results.pre-commit.ci/latest/github/sandman-project/sandman_web/main)

# Sandman Web

Sandman Web is part of the [Sandman Project](https://github.com/sandman-project), which aims to provide a device that allows hospital style beds to be controlled by voice. This component provides a web interface. The web interface currently has the capability to view reports that are automatically collected each day by Sandman. Other features are planned, but have not completed development yet. At the moment, Linux is the only supported operating system.

## Running From Source

First, obtain a copy of the source using your preferred method (for example cloning the repository or downloading a zip).

Sandman web is developed using Flask and is really easy to run with [uv](https://docs.astral.sh/uv). If you have not installed uv, you can find instructions [here](https://docs.astral.sh/uv/getting-started/installation/). Using a command like the following will start the web service in debug mode:

```bash
uv run flask --app sandman_web run --debug --host 0.0.0.0
```

Then in your web browser enter the following URL: YOUR_SANDMAN_IP_ADDRESS:5000. You can stop the web server by pressing CTRL + C in the terminal.

## License

[MIT](https://choosealicense.com/licenses/mit/)
