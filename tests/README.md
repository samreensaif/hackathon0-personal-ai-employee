# Gmail MCP Server - Test Suite

Comprehensive test suite for the Gmail MCP server with both mock tests (safe for CI/CD) and integration tests (require real Gmail API access).

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Categories](#test-categories)
3. [Running Tests](#running-tests)
4. [Configuration](#configuration)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Or install with main project dependencies
pip install pytest pytest-cov pytest-mock python-dotenv
```

### Configure Test Environment

```bash
# Copy the example config
cp tests/.env.test.example tests/.env.test

# Edit with your test email (for integration tests only)
# For mock tests, defaults are fine
```

### Run Tests

```bash
# Run all mock tests (safe, no real API calls)
pytest tests/test_email_mcp.py

# Run with verbose output
pytest tests/test_email_mcp.py -v

# Run integration tests (requires Gmail API setup)
pytest tests/test_email_mcp.py --run-integration

# Run specific test
pytest tests/test_email_mcp.py::TestDraftEmail::test_draft_email_success
```

---

## Test Categories

### 1. Connection Tests (`TestConnection`)

Tests server connectivity and health checks.

**Mock Tests:**
- ✅ Server starts successfully
- ✅ Server stops cleanly
- ✅ Server responds to health checks

**Integration Tests:**
- ⚠️ Real Node.js server starts
- ⚠️ Server responds to actual requests

### 2. Draft Email Tests (`TestDraftEmail`)

Tests draft email creation without sending.

**Mock Tests:**
- ✅ Create draft with valid inputs
- ✅ Fail with missing 'to' field
- ✅ Fail with missing 'subject' field
- ✅ Fail with missing 'body' field
- ✅ Various valid input combinations

**Integration Tests:**
- ⚠️ Create real draft via Gmail API
- ⚠️ Verify draft in Gmail

### 3. Search Email Tests (`TestSearchEmails`)

Tests email search functionality.

**Mock Tests:**
- ✅ Search with valid query
- ✅ Fail with missing query
- ✅ Various Gmail query syntaxes
- ✅ Default max_results
- ✅ Zero results handling

**Integration Tests:**
- ⚠️ Real Gmail search
- ⚠️ Verify search results

### 4. Send Email Tests (`TestSendEmail`)

Tests email sending (most critical).

**Mock Tests:**
- ✅ Send with valid inputs
- ✅ Fail with missing 'to' field
- ✅ Fail with invalid email format
- ✅ Various invalid formats
- ✅ With attachments (if supported)

**Integration Tests:**
- ⚠️ Send real email to test account
- ⚠️ Verify email received

### 5. Error Handling Tests (`TestErrorHandling`)

Tests edge cases and error scenarios.

**Mock Tests:**
- ✅ Server not running
- ✅ Unknown tool
- ✅ Empty arguments
- ✅ Null values

**Integration Tests:**
- ⚠️ Network timeout
- ⚠️ Invalid credentials

### 6. Rate Limiting Tests (`TestRateLimiting`)

Tests quota management and rate limiting.

**Mock Tests:**
- ✅ Multiple rapid requests
- ✅ Quota exceeded simulation

**Integration Tests:**
- ⚠️ Real rate limit errors
- ⚠️ Backoff and retry

### 7. Authentication Tests (`TestAuthentication`)

Tests OAuth2 flow and token management.

**Mock Tests:**
- ✅ Token refresh simulation
- ✅ Missing credentials
- ✅ Invalid credentials format

**Integration Tests:**
- ⚠️ Real OAuth tokens
- ⚠️ Token refresh
- ⚠️ Expired tokens

**Legend:**
- ✅ = Mock test (safe, no real API)
- ⚠️ = Integration test (requires setup)

---

## Running Tests

### Basic Commands

```bash
# All mock tests
pytest tests/test_email_mcp.py

# Verbose output
pytest tests/test_email_mcp.py -v

# Show print statements
pytest tests/test_email_mcp.py -s

# Stop on first failure
pytest tests/test_email_mcp.py -x

# Run last failed tests
pytest tests/test_email_mcp.py --lf

# Run specific test class
pytest tests/test_email_mcp.py::TestDraftEmail

# Run specific test method
pytest tests/test_email_mcp.py::TestDraftEmail::test_draft_email_success
```

### Integration Tests

```bash
# Run with integration tests
pytest tests/test_email_mcp.py --run-integration

# Only integration tests
pytest tests/test_email_mcp.py -m integration

# Exclude integration tests (default behavior)
pytest tests/test_email_mcp.py -m "not integration"
```

### Filtered Tests

```bash
# Only slow tests
pytest tests/test_email_mcp.py -m slow

# Only rate limit tests
pytest tests/test_email_mcp.py -m rate_limit

# Exclude slow tests
pytest tests/test_email_mcp.py -m "not slow"
```

### Coverage Reports

```bash
# Run with coverage
pytest tests/test_email_mcp.py --cov=mcp_servers/email

# HTML coverage report
pytest tests/test_email_mcp.py --cov=mcp_servers/email --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Terminal coverage report
pytest tests/test_email_mcp.py --cov=mcp_servers/email --cov-report=term-missing
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPUs)
pytest tests/test_email_mcp.py -n auto

# Run with specific number of workers
pytest tests/test_email_mcp.py -n 4
```

---

## Configuration

### Environment Variables

Tests use `.env.test` for configuration. Copy the example:

```bash
cp tests/.env.test.example tests/.env.test
```

**Key Settings:**

```bash
# Mock or real API
USE_MOCK_API=true

# Test email addresses
TEST_EMAIL=your-test-email@gmail.com
TEST_RECIPIENT=your-test-email@gmail.com

# Timeouts
SERVER_STARTUP_TIMEOUT=10
TOOL_EXECUTION_TIMEOUT=30

# Cleanup
AUTO_CLEANUP_EMAILS=true
AUTO_CLEANUP_DRAFTS=true
```

### Pytest Configuration

Create `pytest.ini` in project root:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests requiring real Gmail API
    slow: Slow-running tests
    rate_limit: Rate limiting tests
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

---

## Writing Tests

### Test Structure

```python
import pytest

class TestFeature:
    """Test suite for a specific feature."""

    def test_success_case(self, mock_mcp_server, test_email_data):
        """Test successful operation with valid inputs."""
        mock_mcp_server.start()

        result = mock_mcp_server.call_tool('tool_name', {
            'param': 'value'
        })

        assert result['success'] is True
        assert 'expected_field' in result

    def test_error_case(self, mock_mcp_server):
        """Test error handling with invalid inputs."""
        mock_mcp_server.start()

        result = mock_mcp_server.call_tool('tool_name', {})

        assert result['success'] is False
        assert 'error' in result

    @pytest.mark.integration
    def test_real_api(self, real_mcp_server):
        """Integration test with real API."""
        # Requires --run-integration flag
        pass
```

### Using Fixtures

```python
def test_with_fixtures(self, mock_mcp_server, mock_gmail_api, test_email_data):
    """
    Available fixtures:
    - mock_mcp_server: Mock MCP server
    - mock_gmail_api: Mock Gmail API
    - real_mcp_server: Real server instance
    - test_email_data: Sample email data
    - test_config: Test configuration
    """
    pass
```

### Parametrized Tests

```python
@pytest.mark.parametrize("email,should_succeed", [
    ("valid@example.com", True),
    ("invalid", False),
    ("", False),
])
def test_email_validation(self, mock_mcp_server, email, should_succeed):
    """Test with multiple input values."""
    result = mock_mcp_server.call_tool('send_email', {
        'to': email,
        'subject': 'Test',
        'body': 'Test'
    })

    assert result['success'] == should_succeed
```

### Markers

```python
@pytest.mark.integration
def test_integration():
    """Requires --run-integration flag."""
    pass

@pytest.mark.slow
def test_slow():
    """Takes a long time to run."""
    pass

@pytest.mark.rate_limit
def test_rate_limit():
    """Tests rate limiting."""
    pass
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Gmail MCP Server

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'

    - name: Install dependencies
      run: |
        pip install -r tests/requirements.txt
        cd mcp_servers/email && npm install

    - name: Run mock tests
      run: |
        pytest tests/test_email_mcp.py -v --cov=mcp_servers/email

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### GitLab CI Example

```yaml
test:
  image: python:3.10
  before_script:
    - pip install -r tests/requirements.txt
    - curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    - apt-get install -y nodejs
    - cd mcp_servers/email && npm install
  script:
    - pytest tests/test_email_mcp.py -v --cov=mcp_servers/email
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Only Mock Tests in CI

To ensure CI/CD only runs safe mock tests:

```yaml
# GitHub Actions
- name: Run tests
  run: pytest tests/test_email_mcp.py -m "not integration"

# Or explicitly
- name: Run tests
  run: pytest tests/test_email_mcp.py
  # Don't use --run-integration flag
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:**
```bash
pip install -r tests/requirements.txt
```

#### 2. Server Won't Start

**Problem:** Real server tests fail with "Server failed to start"

**Solution:**
```bash
# Verify Node.js is installed
node --version

# Verify dependencies
cd mcp_servers/email && npm install

# Test server manually
node mcp_servers/email/server.js
```

#### 3. Integration Tests Skipped

**Problem:** All integration tests are skipped

**Solution:**
```bash
# Use the --run-integration flag
pytest tests/test_email_mcp.py --run-integration
```

#### 4. OAuth Errors

**Problem:** Integration tests fail with authentication errors

**Solution:**
```bash
# Re-run OAuth setup
cd mcp_servers/email
node auth.js

# Or use Python
python scripts/setup_gmail_oauth.py

# Verify token exists
ls mcp_servers/email/token.json
```

#### 5. Rate Limit Tests Fail

**Problem:** Rate limit tests fail or time out

**Solution:**
```bash
# Disable rate limit tests
pytest tests/test_email_mcp.py -m "not rate_limit"

# Or adjust timeout in .env.test
TOOL_EXECUTION_TIMEOUT=60
```

### Debug Mode

```bash
# Run with full traceback
pytest tests/test_email_mcp.py --tb=long

# Run with pdb on failure
pytest tests/test_email_mcp.py --pdb

# Show local variables on failure
pytest tests/test_email_mcp.py -l

# Disable warnings
pytest tests/test_email_mcp.py --disable-warnings
```

### Test Output

```bash
# Capture stdout/stderr
pytest tests/test_email_mcp.py -s

# Show print statements
pytest tests/test_email_mcp.py --capture=no

# Quiet mode
pytest tests/test_email_mcp.py -q

# Very verbose
pytest tests/test_email_mcp.py -vv
```

---

## Test Checklist

Before committing changes:

- [ ] All mock tests pass
- [ ] Coverage > 80%
- [ ] No hardcoded credentials
- [ ] Integration tests marked with `@pytest.mark.integration`
- [ ] Slow tests marked with `@pytest.mark.slow`
- [ ] Clear test names and docstrings
- [ ] Proper assertions with helpful messages
- [ ] Cleanup code in fixtures
- [ ] Updated this README if needed

---

## Best Practices

### 1. Always Use Mock Tests by Default

```python
# ✅ Good - Safe for CI/CD
def test_feature(self, mock_mcp_server):
    pass

# ❌ Avoid - Only for integration
@pytest.mark.integration
def test_feature(self, real_mcp_server):
    pass
```

### 2. Clear Test Names

```python
# ✅ Good
def test_draft_email_missing_to_field_returns_error(self):
    pass

# ❌ Bad
def test_draft(self):
    pass
```

### 3. Helpful Assertions

```python
# ✅ Good
assert result['success'] is True, f"Expected success but got: {result}"

# ❌ Bad
assert result['success']
```

### 4. Use Fixtures

```python
# ✅ Good
def test_feature(self, mock_mcp_server, test_email_data):
    pass

# ❌ Bad
def test_feature(self):
    server = MockMCPServer()
    data = {'to': 'test@example.com', ...}
```

### 5. Clean Up

```python
@pytest.fixture
def resource():
    # Setup
    r = create_resource()
    yield r
    # Cleanup
    r.cleanup()
```

---

## Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **Gmail API:** https://developers.google.com/gmail/api
- **MCP Specification:** https://modelcontextprotocol.io/
- **Testing Best Practices:** https://docs.pytest.org/en/latest/goodpractices.html

---

## Contributing

When adding new tests:

1. Follow existing test structure
2. Use mock tests by default
3. Mark integration tests properly
4. Add clear docstrings
5. Update this README
6. Ensure all tests pass

---

**Last Updated:** February 2026
**Test Coverage:** 85%+ target
**Total Tests:** 50+ tests
