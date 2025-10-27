# Contributing to Onion Hoster

First off, thank you for considering contributing to Onion Hoster! It's people like you that make Onion Hoster such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Provide specific examples to demonstrate the steps**.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why**.
* **Include screenshots and animated GIFs** if possible.
* **Include your environment details**: OS, Python version, distribution, etc.

#### Bug Report Template

```markdown
**Description:**
A clear and concise description of the bug.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Environment:**
- OS: [e.g. Ubuntu 22.04, Windows 11, macOS Ventura]
- Python Version: [e.g. 3.10.0]
- Onion Hoster Version: [e.g. 1.0.0]
- Tor Version: [e.g. 0.4.7.13]
- Nginx Version: [e.g. 1.18.0]

**Screenshots:**
If applicable, add screenshots to help explain your problem.

**Additional Context:**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps** or provide mockups.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most Onion Hoster users.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include thoughtful comments in your code
* Write meaningful commit messages
* Update documentation if needed
* Add tests if applicable

#### Pull Request Process

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** following our coding standards.
3. **Test your changes** thoroughly:
   - Test on your target platform
   - Test both GUI and CLI modes
   - Ensure existing functionality still works
4. **Update documentation** if you changed functionality.
5. **Commit your changes** with a clear commit message.
6. **Push to your fork** and submit a pull request.
7. **Wait for review** and address any feedback.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Tor (for testing)
- Nginx (for testing)

### Setting Up Development Environment

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Onion-Hoster.git
   cd Onion-Hoster
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies:**
   ```bash
   pip install pytest pylint black flake8 mypy
   ```

5. **Make the launcher executable:**
   ```bash
   chmod +x onion-host
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_system_detector.py
```

### Code Style

We follow PEP 8 with some modifications:

- **Line length:** 100 characters maximum (not 79)
- **Indentation:** 4 spaces (no tabs)
- **Quotes:** Use double quotes for strings
- **Imports:** Group imports (standard library, third-party, local)
- **Docstrings:** Use triple double quotes and follow Google style

#### Formatting Your Code

Before committing, format your code:

```bash
# Format with black
black src/

# Check with flake8
flake8 src/

# Type check with mypy
mypy src/
```

### Commit Message Guidelines

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**
```
feat(gui): add dark mode toggle button

fix(cli): resolve crash when directory path has spaces

docs(readme): update installation instructions for macOS

style(core): format code with black

refactor(service): simplify nginx configuration logic

perf(updater): optimize version checking algorithm

test(detector): add tests for Windows platform detection

chore(deps): update customtkinter to 5.2.1
```

## Project Structure

```
Onion-Hoster/
├── src/
│   ├── core/           # Core functionality
│   │   ├── constants.py        # Configuration constants
│   │   ├── system_detector.py  # OS/environment detection
│   │   ├── config_manager.py   # Configuration management
│   │   ├── onion_service.py    # Service management
│   │   └── update_manager.py   # Update functionality
│   ├── gui/            # GUI interface
│   │   └── gui_app.py          # CustomTkinter application
│   └── cli/            # CLI interface
│       └── cli_interface.py    # Command-line interface
├── config/             # Configuration files
├── assets/             # Application assets
├── tests/              # Unit tests
└── docs/               # Documentation
```

## Areas for Contribution

### High Priority

- [ ] Unit tests for all modules
- [ ] Integration tests
- [ ] Support for more Linux distributions
- [ ] Windows-specific improvements
- [ ] macOS testing and improvements
- [ ] Termux optimization

### Medium Priority

- [ ] Support for dynamic content (PHP, Node.js)
- [ ] Multiple site management
- [ ] Built-in website templates
- [ ] Traffic statistics (privacy-preserving)
- [ ] Backup and restore functionality
- [ ] Docker container support

### Low Priority

- [ ] Custom vanity .onion addresses (requires compilation)
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Internationalization (i18n)
- [ ] Plugin system

### Documentation

- [ ] Video tutorials
- [ ] More screenshots
- [ ] FAQ section
- [ ] Troubleshooting guide
- [ ] API documentation

## Testing Guidelines

### Test Coverage

- Aim for at least 80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions
- Mock external dependencies (Tor, Nginx, network calls)

### Test Structure

```python
"""Test module for SystemDetector class."""

import pytest
from src.core.system_detector import SystemDetector


class TestSystemDetector:
    """Test cases for SystemDetector."""

    def test_detect_os_type(self):
        """Test OS type detection."""
        detector = SystemDetector()
        assert detector.os_type in ["linux", "darwin", "windows"]

    def test_is_tor_installed(self):
        """Test Tor installation detection."""
        detector = SystemDetector()
        # Mock or skip if Tor not installed
        result = detector.is_tor_installed()
        assert isinstance(result, bool)
```

## Documentation Guidelines

### Code Documentation

- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include parameter types and return types
- Provide usage examples for complex functions

```python
def create_nginx_config(site_directory: str, port: int = None) -> Tuple[bool, str]:
    """
    Create Nginx configuration for the onion site.

    Args:
        site_directory: Path to the site directory containing index.html
        port: Nginx port (default from config if not specified)

    Returns:
        Tuple of (success: bool, message: str) indicating result

    Raises:
        PermissionError: If insufficient permissions to write config
        ValueError: If site_directory is invalid

    Example:
        >>> service = OnionServiceManager(config, system)
        >>> success, message = service.create_nginx_config("/var/www/mysite", 8080)
        >>> if success:
        ...     print(f"Config created: {message}")
    """
```

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Update troubleshooting section for known issues
- Keep documentation concise and beginner-friendly

## Review Process

### For Maintainers

When reviewing pull requests:

1. **Check code quality**
   - Follows style guide
   - Has appropriate tests
   - Documentation is updated
   - No breaking changes (or properly documented)

2. **Test the changes**
   - Run automated tests
   - Test manually on multiple platforms if possible
   - Verify security implications

3. **Provide constructive feedback**
   - Be respectful and encouraging
   - Explain the reasoning behind suggestions
   - Approve when ready or request changes

### For Contributors

When your PR is under review:

- Be responsive to feedback
- Be open to suggestions
- Ask questions if something is unclear
- Don't take feedback personally
- Update your PR based on review comments

## Questions?

Feel free to:
- Open an issue with the `question` label
- Start a discussion on GitHub Discussions
- Check existing issues and discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Onion Hoster! 🧅🎉
