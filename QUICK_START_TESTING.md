# Quick Start: Testing Guide

## Installation

```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run all tests (121 tests, ~0.2 seconds)
pytest

# Verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestQuestion::test_question_creation

# Run by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
```

## Coverage

```bash
# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Structure

```
tests/
├── unit/          # 102 fast, isolated tests
├── integration/   # 9 multi-component tests
└── e2e/          # End-to-end tests (to be added)
```

## Key Test Files

| File | Tests | What it Tests |
|------|-------|---------------|
| `test_models.py` | 16 | Question, Student, Evaluation, Class |
| `test_utils.py` | 17 | round_up() function |
| `test_csv_parsing.py` | 12 | CSV parsing with StringIO |
| `test_settings.py` | 11 | GlobalSettings JSON serialization |
| `test_results_core.py` | 41 | **Results core & grading formula** ⭐ |
| `test_results_stats.py` | 10 | Statistics methods |
| `test_interactions.py` | 15 | User interaction mocks |
| `test_csv_io_roundtrip.py` | 9 | CSV file I/O integration |

## Common Tasks

### Add a new test
```python
# In appropriate test file (e.g., tests/unit/test_models.py)
@pytest.mark.unit
def test_my_new_feature(sample_evaluation):
    """Test description."""
    # Test code here
    assert something == expected
```

### Use a fixture
```python
def test_with_fixture(sample_class, sample_evaluation):
    """Fixtures are automatically provided by pytest."""
    results = Results(sample_class, sample_evaluation)
    # Test code here
```

### Test with temporary files
```python
def test_file_operation(tmp_dir):
    """tmp_dir is a temporary directory that's cleaned up after test."""
    file_path = tmp_dir / "test.csv"
    # Write and read file
    # File is automatically cleaned up
```

## Debugging Failed Tests

```bash
# Show full traceback
pytest --tb=long

# Stop at first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Run only failed tests from last run
pytest --lf
```

## Best Practices

1. **Name tests clearly**: `test_<what>_<scenario>`
2. **Use markers**: `@pytest.mark.unit` or `@pytest.mark.integration`
3. **Add docstrings**: Explain what the test validates
4. **Use fixtures**: Don't repeat setup code
5. **Test edge cases**: Not just happy path
6. **Keep tests fast**: Use mocks, avoid file I/O in unit tests

## Current Status

- ✅ **121 tests** passing
- ✅ **0.2 seconds** execution time
- ✅ **~35% coverage** (core modules at 90%+)
- ✅ **Zero regressions** in existing functionality

## Next Steps

To reach 90% coverage:
1. Refactor and test `import_online_csv_to_results()` (Phase 5)
2. Test plotting functions (Phase 4)
3. Add end-to-end workflow tests (Phase 7)

## Getting Help

- See `README_TESTS.md` for comprehensive documentation
- See `IMPLEMENTATION_SUMMARY.md` for implementation status
- See `TEST_IMPLEMENTATION_STATUS.md` for detailed progress
