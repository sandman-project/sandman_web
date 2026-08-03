[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sandman-project/sandman_web/main.svg)](https://results.pre-commit.ci/latest/github/sandman-project/sandman_web/main)

# Sandman Web

Sandman Web is part of the [Sandman Project](https://github.com/sandman-project), which aims to provide a device that allows hospital style beds to be controlled by voice. This component provides a web interface. The web interface currently has the capability to view reports that are automatically collected each day by Sandman. Other features are planned, but have not completed development yet. At the moment, Linux is the only supported operating system.

## Sandman Web Setup

If you are interested in running Sandman Web in development mode, please read [CONTRIBUTING](CONTRIBUTING.md). If you wish to run it in deployment mode, you can use the following instructions. 

Obtain a copy of the source. Then use the following commands to start the Docker container:

```bash
cd ~/sandman_main
```
```bash
docker compose up -d
```

Then in your web browser enter the following URL: YOUR_SANDMAN_IP_ADDRESS:5000.

## License

[MIT](https://choosealicense.com/licenses/mit/)
