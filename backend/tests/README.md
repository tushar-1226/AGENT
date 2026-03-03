# Testing Guide - F.R.I.D.A.Y. Agent

## Overview

This directory contains comprehensive tests for the F.R.I.D.A.Y. Agent backend modules.

## Test Structure

```
tests/
├── conftest.py                  # Pytest configuration and fixtures
├── test_cache_manager.py        # Cache module tests
├── test_code_intelligence.py    # Code intelligence tests
└── test_metrics.py              # Metrics module tests
```

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run with Coverage
```bash
pytest --cov=modules --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_cache_manager.py -v
```

### Run Specific Test
```bash
pytest tests/test_cache_manager.py::TestCacheManager::test_set_and_get -v
```

## Test Coverage

Current coverage: **75%+**

### Module Coverage:
- Cache Manager: 90%+
- Code Intelligence: 85%+
- Metrics: 88%+

## Writing New Tests

### Test File Template
```python
"""
Tests for Module Name
"""

import pytest
from modules.your_module import YourClass

class TestYourClass:
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        obj = YourClass()
        result = obj.method()
        assert result == expected_value
```

### Using Fixtures
```python
def test_with_fixture(sample_code):
    """Test using fixture from conftest.py"""
    # sample_code is automatically provided
    result = analyze(sample_code)
    assert result["success"] is True
```

## Continuous Integration

Tests run automatically on:
- Push to main/develop
- Pull requests
- Manual workflow dispatch

See `.github/workflows/ci.yml` for full CI configuration.

## Coverage Reports

HTML coverage reports are generated in `htmlcov/` directory:
```bash
open htmlcov/index.html
```

## Best Practices

1. **Test Naming**: Use descriptive names (test_feature_behavior)
2. **One Assert per Test**: Keep tests focused
3. **Use Fixtures**: Reuse common setup code
4. **Test Edge Cases**: Don't just test happy paths
5. **Mock External Services**: Don't rely on external APIs
6. **Clean Up**: Use teardown for cleanup

## Common Issues

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest
```

### Async Tests
Use `@pytest.mark.asyncio` for async tests:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Additional Resources

- Pytest Docs: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Testing Best Practices: See CONTRIBUTING.md
