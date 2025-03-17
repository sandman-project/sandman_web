# Contributing to Sandman Web

Everyone is welcome to contribute to Sandman. There is plenty to do. The majority of development communication happens on the Sandman Discord. You can find a link to join the Sandman Discord in the README for the Sandman project.

## Feature Requests

Please make all feature requests in the Sandman Discord. Only use Issues for reporting and resolving issues.

## Development Process

 - If you haven't already, fork the repository. You will not be able to push to main or new branches on the original repository.
 - Write and test your code using a new branch. Please follow the [Coding Standards](CODING-STANDARDS.md).
 - We use Ruff in order to lint and format code. This is set up using pre-commit to automatically check pull requests. Although you don't need to run this as an actual pre-commit hook locally, it's a good idea to run it prior to making a pull request. The easiest way to do that is with [uv](https://docs.astral.sh/uv). If you have not installed uv, you can find instructions [here](https://docs.astral.sh/uv/getting-started/installation/).
 ```bash
 uvx pre-commit run --all-files
 ```
  - Ensure that all the tests pass. Tests will be added soon.