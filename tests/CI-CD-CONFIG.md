# CI/CD Test Configuration

Complete test configuration and execution details for the Commerzbank FinTS Payout Automator CI/CD pipeline.

## Test Suite Overview

### Test Statistics

- **Total Tests**: 113 tests across 6 test files
- **Test Files**: 6 comprehensive test modules
- **Coverage Target**: 85% minimum
- **Execution Time**: 10-15 minutes (parallel execution)
- **Platforms**: Ubuntu, Windows, macOS
- **Python Versions**: 3.11, 3.12

### Test Files Structure

```
tests/
├── conftest.py                    # Test configuration and fixtures
├── test_iban_validation.py       # IBAN validation tests (20+ tests)
├── test_financial_calculations.py # Financial calculation tests (25+ tests)
├── test_thread_coordination.py    # Thread coordination tests (18+ tests)
├── test_data_import.py           # Data import tests (22+ tests)
├── test_error_handling.py        # Error handling tests (28+ tests)
└── README.md                      # Test documentation
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Minimum version
minversion = 7.0

# Execution options
addopts =
    -v                           # Verbose output
    --showlocals                 # Local variables in tracebacks
    -ra                          # Show test summary
    --cov=commerzbank_fints_qt_desktop_app
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=85
    --strict-markers
    --timeout=900               # 15 minutes
    -n auto                      # Parallel execution
    --dist=loadscope
    --junitxml=test-results.xml

testpaths = tests
```

### Test Markers

Tests are categorized using pytest markers:

```python
@pytest.mark.slow           # Slow tests (>5 seconds)
@pytest.mark.integration    # Integration tests
@pytest.mark.unit          # Unit tests
@pytest.mark.gui           # GUI tests (Qt6)
@pytest.mark.threading     # Thread coordination tests
@pytest.mark.financial     # Financial calculation tests
@pytest.mark.iban          # IBAN validation tests
@pytest.mark.error         # Error handling tests
@pytest.mark.import        # Data import tests
@pytest.mark.benchmark     # Performance benchmarks
```

## Test Fixtures

### Qt6 GUI Fixtures

```python
@pytest.fixture
def app_instance():
    """Qt6 QApplication instance for GUI testing."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app

@pytest.fixture
def main_window(app_instance):
    """Main application window fixture."""
    from commerzbank_fints_qt_desktop_app import CommerzbankFinTSApp
    window = CommerzbankFinTSApp()
    yield window
```

### Data Fixtures

```python
@pytest.fixture
def valid_iban():
    """Valid German IBAN for testing."""
    return "DE89370400440532013000"

@pytest.fixture
def invalid_iban():
    """Invalid IBAN for testing."""
    return "DE12345678901234567890"

@pytest.fixture
def sample_payout_data():
    """Sample payout data for testing."""
    return {
        "recipient": "John Doe",
        "iban": "DE89370400440532013000",
        "amount": "100.00",
        "purpose": "Invoice payment"
    }
```

## Test Execution

### Local Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_iban_validation.py -v

# Run specific test
pytest tests/test_iban_validation.py::TestIBANValidation::test_valid_iban

# Run with coverage
pytest tests/ -v --cov=commerzbank_fints_qt_desktop_app

# Run only unit tests
pytest tests/ -m unit -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Run in parallel
pytest tests/ -n auto --dist=loadscope

# Run with timeout
pytest tests/ --timeout=900
```

### CI/CD Execution

```bash
# CI pipeline execution (automated in GitHub Actions)
xvfb-run -a pytest tests/ -v \
    --cov=commerzbank_fints_qt_desktop_app \
    --cov-report=xml \
    --cov-report=html \
    --timeout=900 \
    -n auto \
    --junitxml=test-results.xml
```

## Platform-Specific Testing

### Ubuntu (Linux)

```yaml
System Dependencies:
  - libxkbcommon-x11-0
  - libxcb-cursor0
  - libxcb-xinerama0
  - libgl1-mesa-glx
  - libfontconfig1
  - libglib2.0-0
  - xvfb (for headless GUI testing)

Execution:
  xvfb-run -a pytest tests/ -v
```

### Windows

```yaml
Platform: windows-latest
Execution:
  pytest tests/ -v (Direct Qt6 execution)
```

### macOS

```yaml
Platform: macos-latest
Execution:
  pytest tests/ -v (Direct Qt6 execution)
```

## Coverage Configuration

### Coverage Settings

```ini
[coverage:run]
source = commerzbank_fints_qt_desktop_app
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*
    */dist/*
    */build/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Overall | 85%+ | 85%+ |
| IBAN Validation | 90%+ | 90%+ |
| Financial Calculations | 95%+ | 95%+ |
| Thread Coordination | 85%+ | 85%+ |
| Error Handling | 90%+ | 90%+ |
| Data Import | 85%+ | 85%+ |

## Test Categories

### 1. IBAN Validation Tests (`test_iban_validation.py`)

**Purpose**: Validate IBAN format and checksum logic.

**Test Count**: 20+ tests

**Key Tests**:
- ✅ Valid German IBANs
- ✅ MOD-97 checksum validation
- ✅ Country code validation
- ✅ Length validation
- ✅ Invalid IBAN detection
- ✅ Edge cases and special characters

**Execution Time**: ~30 seconds

### 2. Financial Calculation Tests (`test_financial_calculations.py`)

**Purpose**: Test SEPA payment calculations and formatting.

**Test Count**: 25+ tests

**Key Tests**:
- ✅ Decimal precision handling
- ✅ SEPA XML generation
- ✅ Amount formatting
- ✅ Fee calculations
- ✅ Batch sum calculations
- ✅ Currency conversion (if applicable)

**Execution Time**: ~45 seconds

### 3. Thread Coordination Tests (`test_thread_coordination.py`)

**Purpose**: Ensure proper thread synchronization and UI responsiveness.

**Test Count**: 18+ tests

**Key Tests**:
- ✅ Thread lifecycle management
- ✅ Signal propagation
- ✅ UI thread safety
- ✅ Background task execution
- ✅ Thread cleanup
- ✅ Race condition prevention

**Execution Time**: ~60 seconds

### 4. Data Import Tests (`test_data_import.py`)

**Purpose**: Validate clipboard data import functionality.

**Test Count**: 22+ tests

**Key Tests**:
- ✅ CSV format parsing
- ✅ TSV format parsing
- ✅ Excel clipboard format
- ✅ Data validation
- ✅ Error handling
- ✅ Encoding handling

**Execution Time**: ~40 seconds

### 5. Error Handling Tests (`test_error_handling.py`)

**Purpose**: Comprehensive error scenario coverage.

**Test Count**: 28+ tests

**Key Tests**:
- ✅ Network error handling
- ✅ Authentication failures
- ✅ Invalid input handling
- ✅ File I/O errors
- ✅ Thread exception handling
- ✅ User feedback on errors

**Execution Time**: ~50 seconds

## Performance Testing

### Benchmark Configuration

```bash
# Run benchmark tests
pytest tests/test_financial_calculations.py \
    --benchmark-only \
    --benchmark-json=benchmark-results.json \
    --benchmark-columns=min,max,mean,stddev,ops,rounds
```

### Performance Baselines

| Operation | Target | Threshold |
|-----------|--------|-----------|
| IBAN Validation | <10ms | 20ms |
| Financial Calc | <50ms | 100ms |
| Data Import | <100ms | 200ms |
| Thread Start | <50ms | 100ms |

## Troubleshooting

### Common Test Issues

#### 1. Qt6 GUI Test Failures

**Problem**: Tests fail with Qt application errors

**Solution**:
```bash
# Check QApplication fixture
# Verify single instance logic
# Use xvfb-run on Linux
xvfb-run -a pytest tests/ -v
```

#### 2. Timeout Errors

**Problem**: Tests timeout after 15 minutes

**Solution**:
```bash
# Identify slow tests
pytest tests/ --durations=10

# Run specific tests only
pytest tests/test_specific.py -v

# Increase timeout if needed
# Edit pytest.ini: timeout = 1800  # 30 minutes
```

#### 3. Coverage Failures

**Problem**: Coverage below 85%

**Solution**:
```bash
# Check coverage report
coverage report -m

# Identify gaps
# Add tests for uncovered code
# Verify test execution
pytest tests/ -v --cov=commerzbank_fints_qt_desktop_app
```

#### 4. Parallel Execution Issues

**Problem**: Tests fail when run in parallel

**Solution**:
```bash
# Run sequentially to debug
pytest tests/ -n 1 -v

# Check for shared state issues
# Verify fixture isolation
# Review thread safety
```

## Test Maintenance

### Adding New Tests

1. **Create test file**: `tests/test_new_feature.py`
2. **Add fixtures**: Use existing fixtures or create new ones
3. **Mark tests**: Apply appropriate markers
4. **Update documentation**: Update this file

### Test Review Checklist

- [ ] All tests passing locally
- [ ] Coverage threshold met (85%+)
- [ ] No test interdependencies
- [ ] Proper cleanup in fixtures
- [ ] Appropriate test markers
- [ ] Error cases covered
- [ ] Edge cases tested
- [ ] Performance acceptable

## CI/CD Integration

### GitHub Actions Integration

The test suite is automatically executed in GitHub Actions with:

1. **Multi-Platform Testing**: Ubuntu, Windows, macOS
2. **Parallel Execution**: pytest-xdist with auto workers
3. **Coverage Reporting**: XML and HTML reports
4. **Artifact Storage**: Test results and coverage data
5. **PR Comments**: Automatic test summaries on pull requests

### Quality Gates

Tests must pass all quality gates before merge:

- ✅ All 113 tests passing
- ✅ Coverage ≥85%
- ✅ No security vulnerabilities
- ✅ Code quality checks passing
- ✅ Performance benchmarks stable

## Continuous Improvement

### Test Metrics Tracking

- **Test Execution Time**: Monitor and optimize
- **Test Success Rate**: Target >98%
- **Coverage Trends**: Maintain or increase
- **Flaky Test Rate**: Target <1%
- **Performance Regression**: Detect automatically

### Optimization Strategies

1. **Parallel Execution**: Already enabled
2. **Fixture Optimization**: Proper setup/teardown
3. **Test Isolation**: No interdependencies
4. **Selective Testing**: Use markers for focused testing

---

**Last Updated**: 2025-06-20
**Version**: 1.0.0
**Maintained By**: @CJ-1981
