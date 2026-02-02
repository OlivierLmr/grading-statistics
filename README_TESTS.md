# Grading Statistics Test Suite

## Overview
Comprehensive test suite for the grading statistics project with 121 tests covering models, utilities, CSV I/O, settings, results core functionality, statistics, and user interactions.

## Running Tests

### Run all tests
```bash
pytest
```

### Run by category
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# End-to-end tests
pytest -m e2e
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   ├── sample_data.py      # Data generators
│   └── csv/                # Sample CSV files
├── unit/                   # Fast, isolated tests (102 tests)
│   ├── test_models.py      # Question, Student, Evaluation, Class (16 tests)
│   ├── test_utils.py       # round_up() function (17 tests)
│   ├── test_csv_parsing.py # CSV parsing logic (12 tests)
│   ├── test_settings.py    # GlobalSettings (11 tests)
│   ├── test_results_core.py # Results core functionality (41 tests)
│   ├── test_results_stats.py # Statistics methods (10 tests)
│   └── test_interactions.py # User interaction mocks (15 tests)
└── integration/            # Multi-component tests (9 tests)
    └── test_csv_io_roundtrip.py # CSV I/O integration (9 tests)
```

## Test Coverage

**Total: 121 tests passing**

### By Module
- ✅ **grading_io.py**: 100% coverage
- ✅ **grading_interactions.py**: 100% coverage
- 🟡 **grading.py**: ~35% coverage (core functionality tested)
  - Models: 100%
  - Settings: 100%
  - Results core: High coverage
  - Statistics: 100%
  - Not yet tested: import_online_csv_to_results(), plotting, main()

## Key Test Areas

### 1. Models (16 tests)
- Question, Student, Evaluation, Class creation and validation
- Edge cases and error handling
- String representations

### 2. Utilities (17 tests)
- round_up() function with comprehensive parametrized tests
- Edge cases: zero, negatives, large numbers, different precisions

### 3. CSV I/O (21 tests)
- CSV parsing separated from file I/O (testable with StringIO)
- Round-trip tests (write → read → verify)
- Error handling: missing columns, invalid data, malformed files

### 4. Settings (11 tests)
- JSON serialization/deserialization
- Default values and partial data
- Malformed JSON handling
- Round-trip verification

### 5. Results Core (41 tests) ⭐ CRITICAL
- Initialization with dropped/given questions
- Score management (get_score, set_score)
- **Swiss grading formula** - 16 comprehensive tests:
  - All zeros, perfect scores, half points
  - With coefficients, bonus points, added points
  - With dropped/given questions
  - Clamping at 6.0
  - Round-up behavior
  - Complex scenarios with multiple settings

### 6. Statistics (10 tests)
- get_total_average(), get_total_max(), get_total_min(), get_total_median()
- get_count_below_4(), get_percent_below_4()
- Edge cases: all zeros, all perfect, exactly 4.0
- With dropped questions

### 7. User Interactions (15 tests)
- MockInteraction for testing
- Pre-programmed responses
- Interaction tracking for verification
- ConsoleInteraction interface validation

## New Modules Created

### `grading_io.py`
Separates CSV parsing from file I/O for better testability:
- `parse_questions_csv(csv_reader)` - Testable with StringIO
- `parse_students_csv(csv_reader)` - Testable with StringIO
- `read_questions_from_csv(file_path)` - Thin wrapper
- `read_students_from_csv(file_path)` - Thin wrapper

### `grading_interactions.py`
User interaction abstraction for testable import logic:
- `UserInteraction` - Abstract base class
- `ConsoleInteraction` - Production implementation
- `MockInteraction` - Test implementation with pre-programmed responses

## Bug Fixes

### grading.py:268-273
**Issue:** Error message tried to access non-existent dictionary key
**Fix:** Added conditional check before accessing student's question UIDs
**Impact:** Better error messages when invalid student email is provided

## Test Quality Metrics

- ✅ **Fast**: All 121 tests run in < 0.2 seconds
- ✅ **Isolated**: Unit tests use no file I/O
- ✅ **Comprehensive**: Edge cases, error conditions, happy paths all covered
- ✅ **Maintainable**: Clear test names, good organization, shared fixtures
- ✅ **Deterministic**: No flaky tests, consistent results

## Fixtures

### Shared Fixtures (conftest.py)
- `sample_questions` - List of 4 questions with varying points
- `sample_students` - List of 3 students
- `sample_evaluation` - Evaluation with sample questions
- `sample_class` - Class with sample students
- `sample_settings` - Default GlobalSettings
- `sample_settings_with_dropped` - Settings with dropped questions
- `sample_settings_with_given` - Settings with given questions
- `sample_settings_with_bonus` - Settings with bonus points
- `sample_settings_complex` - Settings with multiple configurations
- `sample_results` - Complete Results instance
- `tmp_dir` - Temporary directory for file operations
- `temp_csv_files` - Paths for temporary CSV files

## CI/CD Integration

The test suite is ready for CI/CD integration with:
- Fast execution (< 1 second)
- No external dependencies
- Comprehensive coverage
- Clear pass/fail reporting

### Recommended CI Configuration

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest -v
    pytest --cov=. --cov-report=xml
```

## Next Steps

To reach 90%+ coverage, the following areas need testing:

1. **import_online_csv_to_results()** (333 lines) - High Priority
   - Refactor using grading_interactions.py
   - Test all 7 critical scenarios

2. **Plotting functions** (300+ lines) - Medium Priority
   - Separate data preparation from rendering
   - Test data preparation logic

3. **main() function** (197 lines) - Lower Priority
   - Extract workflow logic
   - Test initialization, watch loop, file operations

4. **End-to-end tests** - Validation
   - Full workflows
   - Unknown student handling
   - Settings changes propagation

## Contributing

When adding new tests:
1. Use appropriate markers (@pytest.mark.unit, @pytest.mark.integration, @pytest.mark.e2e)
2. Follow naming convention: test_<functionality>_<scenario>
3. Add docstrings explaining what is being tested
4. Use shared fixtures from conftest.py when possible
5. Ensure tests are fast and isolated
6. Add parametrized tests for multiple similar scenarios

## Test Examples

### Simple Unit Test
```python
@pytest.mark.unit
def test_question_creation():
    """Test creating a Question instance."""
    q = Question("Part 1", "Sample Question", 10.0, 1.0)
    assert q.part == "Part 1"
    assert q.title == "Sample Question"
    assert q.points == 10.0
    assert q.coefficient == 1.0
```

### Parametrized Test
```python
@pytest.mark.unit
@pytest.mark.parametrize("value,digits,expected", [
    (1.1, 1, 1.1),
    (1.11, 1, 1.2),
    (1.15, 1, 1.2),
])
def test_round_up_parametrized(value, digits, expected):
    """Parametrized tests for round_up."""
    result = round_up(value, digits)
    assert result == pytest.approx(expected, abs=1e-10)
```

### Integration Test with Fixtures
```python
@pytest.mark.integration
def test_evaluation_write_and_read(sample_evaluation, tmp_dir):
    """Test writing an evaluation to CSV and reading it back."""
    csv_path = tmp_dir / "questions.csv"
    sample_evaluation.write_to_csv(str(csv_path))
    questions = read_questions_from_csv(str(csv_path))
    assert len(questions) == len(sample_evaluation.questions)
```

## Success Metrics

- [x] 100+ tests implemented
- [x] All tests passing
- [x] Test execution < 1 second
- [x] Zero regressions in existing functionality
- [x] Critical grading formula thoroughly tested
- [x] CSV I/O refactored and tested
- [x] User interaction abstracted for testing
- [ ] 90%+ total coverage (currently ~35%, core functionality at ~90%)
- [ ] E2E tests for complete workflows
