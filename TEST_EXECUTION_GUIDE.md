# Test Execution Guide

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-test.txt
pip install -r requirements.txt  # Production dependencies
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_iban_validation.py

# Run with coverage
pytest --cov=commerzbank_fints_qt_desktop_app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_iban_validation.py::TestIBANValidationValidCases::test_german_iban_valid_checksum
```

### 3. View Results

```bash
# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Categories

### Run by Category

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only threading tests
pytest -m threading

# Run only financial calculation tests
pytest -m financial

# Run only GUI tests
pytest -m gui

# Skip slow tests
pytest -m "not slow"
```

## Detailed Test Commands

### IBAN Validation Tests

```bash
# Run all IBAN validation tests
pytest tests/test_iban_validation.py

# Run valid IBAN test cases
pytest tests/test_iban_validation.py::TestIBANValidationValidCases

# Run invalid IBAN test cases
pytest tests/test_iban_validation.py::TestIBANValidationInvalidCases

# Run MOD-97 algorithm tests
pytest tests/test_iban_validation.py::TestMOD97AlgorithmCorrectness
```

### Thread Coordination Tests

```bash
# Run all thread coordination tests
pytest tests/test_thread_coordination.py

# Run worker lifecycle tests
pytest tests/test_thread_coordination.py::TestFinTSWorkerThreadLifecycle

# Run signal-slot tests
pytest tests/test_thread_coordination.py::TestSignalSlotCommunication

# Run TAN synchronization tests
pytest tests/test_thread_coordination.py::TestTANEventSynchronization
```

### Financial Calculation Tests

```bash
# Run all financial calculation tests
pytest tests/test_financial_calculations.py

# Run Decimal precision tests
pytest tests/test_financial_calculations.py::TestDecimalPrecision

# Run batch total tests
pytest tests/test_financial_calculations.py::TestBatchTotalCalculations

# Run currency formatting tests
pytest tests/test_financial_calculations.py::TestCurrencyFormatting
```

### Data Import Tests

```bash
# Run all data import tests
pytest tests/test_data_import.py

# Run clipboard parsing tests
pytest tests/test_data_import.py::TestClipboardParsing

# Run table operations tests
pytest tests/test_data_import.py::TestTableRowOperations

# Run batch calculation update tests
pytest tests/test_data_import.py::TestBatchCalculationUpdates
```

### Error Handling Tests

```bash
# Run all error handling tests
pytest tests/test_error_handling.py

# Run FinTS exception tests
pytest tests/test_error_handling.py::TestFinTSLibraryExceptions

# Run input validation tests
pytest tests/test_error_handling.py::TestInputValidation

# Run network failure tests
pytest tests/test_error_handling.py::TestNetworkFailureSimulation
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=commerzbank_fints_qt_desktop_app \
                 --cov-report=xml \
                 --cov-report=html \
                 --cov-fail-under=85

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### GitLab CI

```yaml
test:
  image: python:3.11
  before_script:
    - pip install -r requirements-test.txt
    - pip install -r requirements.txt
  script:
    - pytest --cov=commerzbank_fints_qt_desktop_app --cov-report=xml --cov-report=html
  coverage: '/TOTAL\s+\d+%\s+\d+/'
  artifacts:
    paths:
      - htmlcov/
```

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Ensure project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Qt Display Issues

If Qt tests fail due to display issues:

```bash
# Use offscreen platform
export QT_QPA_PLATFORM=offscreen
pytest
```

### Timing Issues

If GUI tests fail due to timing:

```bash
# Increase Qt wait signal timeout
pytest --qt-wait-signal=5000
```

### Flaky Tests

If tests are flaky:

```bash
# Run tests multiple times
pytest --count=5

# Use pytest-rerunfailures
pip install pytest-rerunfailures
pytest --reruns=3
```

## Test Output Interpretation

### Understanding Test Results

```bash
$ pytest -v

=========================================================================================
test session starts
=========================================================================================
collected 150 items

tests/test_iban_validation.py::TestIBANValidationValidCases::test_german_iban_valid_checksum PASSED [ 0%]
tests/test_iban_validation.py::TestIBANValidationValidCases::test_iban_with_spaces PASSED [ 1%]
tests/test_thread_coordination.py::TestFinTSWorkerThreadLifecycle::test_worker_thread_initialization PASSED [ 2%]
...

=========================================================================================
150 passed in 25.34s
=========================================================================================
```

### Coverage Report

```bash
$ pytest --cov

Name                                                 Stmts   Miss  Cover
------------------------------------------------------------------------------
commerzbank_fints_qt_desktop_app.py                    689     45    93%
tests/conftest.py                                       250      0   100%
tests/test_iban_validation.py                           180      0   100%
...
------------------------------------------------------------------------------
TOTAL                                                   1500    85    94%
```

## Performance Tips

### Parallel Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Skip Slow Tests

```bash
# Skip tests marked as slow
pytest -m "not slow"

# Or run only slow tests
pytest -m slow
```

### Cache Test Results

```bash
# Use pytest cache (automatically enabled)
# Clear cache if needed
pytest --cache-clear
```

## Development Workflow

### Before Committing

```bash
# Run full test suite
pytest

# Check coverage
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html

# Ensure coverage is >= 85%
```

### Writing New Tests

1. Add test file to `tests/` directory
2. Import necessary fixtures from `conftest.py`
3. Follow naming convention: `test_<functionality>_<scenario>`
4. Add appropriate markers
5. Update this guide if adding new test categories

### Test Checklist

Before considering tests complete:

- [ ] All tests pass
- [ ] Coverage >= 85%
- [ ] No flaky tests
- [ ] Tests are independent
- [ ] Tests have descriptive names
- [ ] Edge cases are covered
- [ ] Error cases are tested

## Advanced Usage

### Profiling Tests

```bash
# Profile test execution
pip install pytest-profile
pytest --profile

# View profile
pytest --profile --profile-svg
```

### Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on specific test
pytest --pdb --trace <test_file>::<test_function>

# Use ipdb for better debugging
pip install ipdb
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Custom Markers

Add custom markers in `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    custom: marks tests as custom category
```

Use markers in tests:

```python
import pytest

@pytest.mark.custom
def test_custom_functionality():
    pass
```

Run marked tests:

```bash
pytest -m custom
```

## Continuous Monitoring

### Coverage Trends

Track coverage over time:

```bash
# Generate baseline coverage
pytest --cov --cov-report=xml > baseline_coverage.txt

# Compare with current coverage
pytest --cov --cov-report=xml > current_coverage.txt
diff baseline_coverage.txt current_coverage.txt
```

### Test History

Maintain test history:

```bash
# Save test results
pytest > test_results_$(date +%Y%m%d).txt

# Compare results over time
```

## Support

For issues or questions:

1. Check test output for specific error messages
2. Review fixture definitions in `conftest.py`
3. Consult pytest documentation: https://docs.pytest.org/
4. Review pytest-qt documentation: https://pytest-qt.readthedocs.io/

## License

This test suite is part of the Commerzbank FinTS Payout Automator project.
