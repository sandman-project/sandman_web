# Contributing to Sandman Web

Everyone is welcome to contribute to Sandman. There is plenty to do. The majority of development communication happens on the Sandman Discord. You can find a link to join the Sandman Discord in the README for the Sandman project.

## Feature Requests

Please make all feature requests in the Sandman Discord. Only use Issues for reporting and resolving issues.

## Development Process

 - If you haven't already, fork the repository. You will not be able to push to main or new branches on the original repository.
 - Sandman development uses [uv](https://docs.astral.sh/uv). If you have not installed uv, you can find instructions [here](https://docs.astral.sh/uv/getting-started/installation/).
 - To run Sandman web in debug using uv, you can use the following command from the repository root. 
  ```bash
  uv run flask --app sandman_web run --debug --host 0.0.0.0
  ```
 - Write and test your code using a new branch. Please follow the [Coding Standards](CODING-STANDARDS.md).
 - We use Ruff in order to lint and format code. This is set up using pre-commit to automatically check pull requests. Although you don't need to run this as an actual pre-commit hook locally, it's a good idea to run it prior to making a pull request. To run the pre-commit hook with uv you can use the following command from the repository root.
 ```bash
 uvx pre-commit run --all-files
 ```
 - We use mypy to perform STRICT type checking on non-test code. To run mypy with uv, you can use the following command from the repository root.
 ```bash
 uv run mypy
  ```
 - Add any relevant tests. Ensure that all the tests pass. To run the tests with uv, you can use the following command from the repository root.
 ```bash
 uv run pytest
 ```
 - Open a pull request. Please try to keep pull requests as small and logically coherent as makes sense. That will help make them easier to review.