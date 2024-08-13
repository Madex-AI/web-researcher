# Web Researcher

This project is a Python package that uses Poetry for dependency management and packaging.

## Table of Contents
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Development Environment](#development-environment)
    - [Visual Studio Code](#visual-studio-code)
    - [JetBrains IDEs (IntelliJ IDEA and PyCharm)](#jetbrains-ides-intellij-idea-and-pycharm)
- [Coding Conventions](#coding-conventions)
- [Linting and Testing](#linting-and-testing)
- [Commit Conventions](#commit-conventions)
- [Available Commands](#available-commands)
- [Environment Variables](#environment-variables)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python (version 3.7 or higher)
- Poetry
- Node.js (for environment variable management)
- Make

### Installation

1. **Install Python:**
    - Visit the [official Python website](https://www.python.org/downloads/) and download the latest version for your operating system.
    - Run the installer and follow the prompts. Make sure to check the box that says "Add Python to PATH" during installation.

2. **Install Poetry:**
    - Open a terminal or command prompt.
    - Run the following command:
      ```
      curl -sSL https://install.python-poetry.org | python3 -
      ```
    - For Windows, you may need to use PowerShell and run:
      ```
      (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
      ```

3. **Clone the repository:**
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

4. **Set up the project:**
   ```
   make poetry
   make env
   ```

## Development Environment

This project can be developed using various IDEs. Here are setup instructions for popular choices:

### Visual Studio Code

1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. Open the project folder in VS Code.
3. Install the following extensions:
    - Python
    - PyLance
    - Poetry
4. Configure the Python interpreter:
    - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS).
    - Type "Python: Select Interpreter" and choose the interpreter from your Poetry virtual environment.

### JetBrains IDEs (IntelliJ IDEA and PyCharm)

1. Install [IntelliJ IDEA](https://www.jetbrains.com/idea/) or [PyCharm](https://www.jetbrains.com/pycharm/).
2. Open the project folder in your chosen IDE.
3. Configure the Python interpreter:
    - Go to File > Project Structure > SDKs.
    - Add a new Python SDK, pointing to the interpreter in your Poetry virtual environment.
4. Install the "Poetry" plugin:
    - Go to File > Settings > Plugins (on macOS: IntelliJ IDEA > Preferences > Plugins).
    - Search for "Poetry" and install the plugin.
    - Restart the IDE when prompted.

## Coding Conventions

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Key points include:

- Use 4 spaces per indentation level.
- Limit all lines to a maximum of 79 characters for code and 72 for docstrings/comments.
- Use snake_case for function and variable names.
- Use CamelCase for class names.
- Use UPPERCASE for constants.
- Surround top-level functions and classes with two blank lines.

For a complete guide, please refer to the [PEP 8 documentation](https://www.python.org/dev/peps/pep-0008/).

## Linting and Testing

### Importance of Linting and Testing

Linting and testing are crucial for maintaining code quality and preventing bugs:

- **Linting** helps ensure code consistency, catches potential errors, and enforces style guidelines. It makes the codebase more readable and maintainable.
- **Testing** verifies that your code works as expected, helps catch bugs early, and makes it easier to refactor code with confidence.

### Running Linting and Tests

- To run linting:
  ```
  make lint
  ```

- To run tests:
  ```
  make test
  ```

Always run both linting and tests before committing your changes.

## Commit Conventions

This project uses the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. This leads to more readable messages that are easy to follow when looking through the project history.

### Commit Message Format

Each commit message consists of a **header**, a **body** and a **footer**. The header has a special format that includes a **type**, a **scope** and a **subject**:

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

The **header** is mandatory and the **scope** of the header is optional.

### Example

```
feat(auth): add login functionality

Implement user authentication using JWT tokens.
- Add login route
- Create JWT token generation utility
- Update user model with password hashing

Closes #123
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

## Available Commands

Use the following `make` commands to manage the project:

- `make poetry`: Create virtual environment and install dependencies
- `make env`: Pull environment variables
- `make lint`: Run linting on source files
- `make test`: Run tests
- `make clean`: Clean generated files

## Environment Variables

This project uses `dotenv-vault` for managing environment variables. To set up your environment:

1. Install `dotenv-vault` globally:
   ```
   npm install -g dotenv-vault
   ```

2. Pull the environment variables:
   ```
   make env
   ```

This will create `.env` and `.env.local` files with the necessary environment variables.

---

For more detailed information about specific components or processes, please refer to the project documentation or contact the project maintainers.