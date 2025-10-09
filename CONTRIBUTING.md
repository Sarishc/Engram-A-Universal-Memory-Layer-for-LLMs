# Contributing to Engram

Thank you for your interest in contributing to Engram! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/engram.git
   cd engram
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-org/engram.git
   ```
4. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- PostgreSQL (or use Docker)

### Local Development

1. **Set up the development environment**:
   ```bash
   make venv
   make install
   ```

2. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Set up the database**:
   ```bash
   make docker-up  # Start PostgreSQL, Redis, ChromaDB
   make migrate    # Run database migrations
   ```

4. **Install pre-commit hooks**:
   ```bash
   make pre-commit-install
   ```

5. **Run the development server**:
   ```bash
   make dev
   ```

### Docker Development

1. **Start all services**:
   ```bash
   make docker-up
   ```

2. **Run tests**:
   ```bash
   docker-compose exec api pytest
   ```

## Contributing Guidelines

### Types of Contributions

We welcome contributions in the following areas:

- **Bug fixes**: Fix issues in existing functionality
- **New features**: Add new capabilities to Engram
- **Performance improvements**: Optimize existing code
- **Documentation**: Improve docs, examples, and guides
- **Tests**: Add or improve test coverage
- **Infrastructure**: CI/CD, Docker, deployment improvements

### Development Workflow

1. **Create an issue** (for significant changes) or work on an existing issue
2. **Create a feature branch** from `main`
3. **Make your changes** following our coding standards
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Run quality checks** locally
7. **Submit a pull request**

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**:
   ```bash
   make test
   ```

2. **Run code quality checks**:
   ```bash
   make lint
   make fmt
   ```

3. **Check test coverage**:
   ```bash
   make test-cov
   ```

4. **Update documentation** if needed

5. **Add your changes to CHANGELOG.md**

### Pull Request Template

When submitting a PR, please include:

- **Description**: Clear description of changes
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: How you tested the changes
- **Breaking Changes**: Any breaking changes
- **Related Issues**: Link to related issues

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Approval** from at least one maintainer
4. **Merge** to main branch

## Issue Guidelines

### Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, dependencies
- **Steps to reproduce**: Clear, minimal steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error traces
- **Additional context**: Screenshots, logs, etc.

### Feature Requests

When requesting features, please include:

- **Problem description**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've considered
- **Additional context**: Use cases, examples, etc.

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority:high`: High priority
- `priority:low`: Low priority

## Coding Standards

### Python Style

We use the following tools for code quality:

- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

### Code Style Guidelines

1. **Follow PEP 8** with some modifications:
   - Line length: 88 characters
   - Use type hints for all functions
   - Use descriptive variable names
   - Write docstrings for all public functions

2. **Import organization**:
   ```python
   # Standard library imports
   import os
   from typing import List, Dict
   
   # Third-party imports
   import fastapi
   from pydantic import BaseModel
   
   # Local imports
   from engram.core.memory_store import MemoryStore
   from engram.utils.config import get_settings
   ```

3. **Error handling**:
   ```python
   try:
       result = risky_operation()
   except SpecificException as e:
       logger.error(f"Operation failed: {e}")
       raise ValueError(f"Operation failed: {e}") from e
   ```

4. **Logging**:
   ```python
   from engram.utils.logger import get_logger
   
   logger = get_logger(__name__)
   
   logger.debug("Detailed debug information")
   logger.info("General information")
   logger.warning("Warning message")
   logger.error("Error occurred", exc_info=True)
   ```

### Database Guidelines

1. **Use SQLAlchemy 2.0 style**:
   ```python
   # Good
   result = session.execute(select(User).where(User.id == user_id)).scalar_one()
   
   # Avoid
   result = session.query(User).filter(User.id == user_id).first()
   ```

2. **Use proper migrations**:
   - Create migrations with Alembic
   - Test migrations on sample data
   - Include rollback instructions

3. **Index considerations**:
   - Add indexes for frequently queried columns
   - Consider composite indexes for multi-column queries
   - Monitor query performance

## Testing

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_api.py          # API endpoint tests
├── test_memory_store.py # Core functionality tests
├── test_retrieval.py    # Retrieval engine tests
├── test_consolidation.py # Consolidation tests
└── test_vectordb.py     # Vector database tests
```

### Writing Tests

1. **Use descriptive test names**:
   ```python
   def test_retrieve_memories_with_empty_query_returns_empty_list():
       """Test that empty query returns no results."""
   ```

2. **Use fixtures** for common setup:
   ```python
   @pytest.fixture
   def sample_memory_data():
       return {
           "tenant_id": "test-tenant",
           "user_id": "test-user",
           "texts": ["Test memory"],
       }
   ```

3. **Test edge cases**:
   - Empty inputs
   - Invalid inputs
   - Error conditions
   - Boundary values

4. **Mock external dependencies**:
   ```python
   @patch('engram.providers.openai.OpenAI')
   def test_openai_provider(mock_openai):
       # Test with mocked OpenAI client
   ```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
make test-cov

# Run integration tests
pytest tests/ -m integration

# Run only fast tests
pytest tests/ -m "not slow"
```

### Test Coverage

We aim for **80%+ test coverage**. Coverage reports are generated in `htmlcov/` after running tests.

## Documentation

### Code Documentation

1. **Docstrings**: Use Google style:
   ```python
   def retrieve_memories(
       self,
       tenant_id: str,
       user_id: str,
       query: str,
       top_k: int = 12,
   ) -> List[Dict[str, Any]]:
       """Retrieve semantically relevant memories for a query.
       
       Args:
           tenant_id: Tenant identifier
           user_id: User identifier
           query: Query text for semantic search
           top_k: Maximum number of results to return
           
       Returns:
           List of memory dictionaries with scores
           
       Raises:
           ValueError: If retrieval fails
       """
   ```

2. **Type hints**: Always include type hints:
   ```python
   from typing import List, Dict, Optional
   
   def process_memories(
       memories: List[Memory],
       options: Optional[Dict[str, Any]] = None,
   ) -> List[ProcessedMemory]:
   ```

### API Documentation

- Update OpenAPI documentation in route handlers
- Include examples in request/response models
- Document error conditions and status codes

### User Documentation

- Update README.md for new features
- Add examples to `examples/` directory
- Update architecture docs for significant changes

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Changelog

Update `CHANGELOG.md` with:
- New features
- Bug fixes
- Breaking changes
- Deprecations
- Security updates

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Tagged and released
- [ ] Docker images built
- [ ] Announcement posted

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Real-time chat (if available)
- **Email**: For security issues

## License

By contributing to Engram, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Engram! Your contributions help make this project better for everyone.
