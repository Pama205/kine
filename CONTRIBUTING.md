# Contributing Guide

Thank you for your interest in contributing to **kine**! This document explains how you can help improve the project.

## How to Contribute

### 1. Report Bugs
- Open a [new Issue](https://github.com/Pama205/kine/issues) with the `bug` label.
- Use the following format:
  ```markdown
  ### Description
  [Clearly describe the bug]

  ### Steps to Reproduce
  1. ...
  2. ...

  ### Expected Behavior
  [What should happen?]

  ### Screenshots / logs (optional)
  ```

### 2. Propose Enhancements
- Discuss major changes in an Issue before submitting a PR.
- Explain the problem your proposal solves.

### 3. Submit Pull Requests
1. Fork the repository: https://github.com/Pama205/kine
2. Create a descriptive branch: `git checkout -b feature/my-feature`
3. Write clear commits following [Conventional Commits](https://www.conventionalcommits.org/)
4. Make sure all checks pass:
   ```bash
   poetry run pytest -v
   poetry run black --check src tests
   poetry run isort --check-only src tests
   poetry run mypy src
   ```
5. Open a Pull Request with a detailed description.

## Code Standards
- Follow the architecture documented in `docs/ARCHITECTURE.md`
- All I/O operations must be `async` (`async def` / `await`)
- Use Pydantic for all public data structures
- Write tests with mocks; never call real APIs in unit tests
- The engine depends on abstractions (`IAProvider` protocol), never on concrete providers

## License
By contributing, you agree that your code will be published under the MIT license.
