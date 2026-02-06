# Quick Start - Gmail MCP Server Testing

Get your test suite running in 2 minutes!

---

## 🚀 Super Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install -r tests/requirements.txt

# 2. Run tests
pytest tests/test_email_mcp.py

# Done! ✓
```

---

## 📋 What Just Happened?

You ran **50+ mock tests** that validate:
- ✅ Email drafting
- ✅ Email search
- ✅ Email sending
- ✅ Error handling
- ✅ Rate limiting
- ✅ Authentication

**All without making real API calls!** Safe for CI/CD.

---

## 🎯 Common Commands

```bash
# All tests (mock only)
pytest tests/test_email_mcp.py

# With coverage report
pytest tests/test_email_mcp.py --cov=mcp_servers/email

# Verbose output
pytest tests/test_email_mcp.py -v

# Stop on first failure
pytest tests/test_email_mcp.py -x

# Re-run failed tests
pytest tests/test_email_mcp.py --lf
```

---

## 🔧 Using Test Runners

### Linux/macOS/WSL

```bash
# Make executable (first time)
chmod +x tests/run_tests.sh

# Run all tests
./tests/run_tests.sh all

# Run with coverage
./tests/run_tests.sh coverage

# Run specific test
./tests/run_tests.sh specific TestDraftEmail::test_draft_email_success

# Clean artifacts
./tests/run_tests.sh clean
```

### Windows

```cmd
REM Run all tests
tests\run_tests.bat all

REM Run with coverage
tests\run_tests.bat coverage

REM Run specific test
tests\run_tests.bat specific TestDraftEmail::test_draft_email_success

REM Clean artifacts
tests\run_tests.bat clean
```

---

## 🧪 Integration Tests (Optional)

Integration tests require real Gmail API access.

### Setup

1. **Configure Gmail OAuth:**
   ```bash
   cd mcp_servers/email
   node auth.js
   # Follow prompts
   ```

2. **Update test config:**
   ```bash
   cp tests/.env.test.example tests/.env.test
   # Edit TEST_EMAIL with your address
   ```

3. **Run integration tests:**
   ```bash
   pytest tests/test_email_mcp.py --run-integration
   ```

---

## 📊 Coverage Report

```bash
# Generate HTML coverage report
pytest tests/test_email_mcp.py --cov=mcp_servers/email --cov-report=html

# Open in browser
open htmlcov/index.html       # macOS
xdg-open htmlcov/index.html   # Linux
start htmlcov\index.html      # Windows
```

**Target:** 80%+ coverage

---

## 🎨 Test Markers

Filter tests by marker:

```bash
# Only integration tests
pytest tests/test_email_mcp.py -m integration

# Exclude integration tests (default)
pytest tests/test_email_mcp.py -m "not integration"

# Only slow tests
pytest tests/test_email_mcp.py -m slow

# Exclude slow tests
pytest tests/test_email_mcp.py -m "not slow"

# Only rate limit tests
pytest tests/test_email_mcp.py -m rate_limit
```

---

## 🐛 Debugging Tests

```bash
# Drop into debugger on failure
pytest tests/test_email_mcp.py --pdb

# Show local variables on failure
pytest tests/test_email_mcp.py -l

# Full traceback
pytest tests/test_email_mcp.py --tb=long

# Show print statements
pytest tests/test_email_mcp.py -s
```

---

## 📁 Test Structure

```
tests/
├── test_email_mcp.py          # Main test file (50+ tests)
├── requirements.txt           # Test dependencies
├── .env.test                  # Test configuration
├── README.md                  # Full documentation
├── QUICK_START_TESTING.md     # This file
├── run_tests.sh               # Test runner (Linux/macOS)
└── run_tests.bat              # Test runner (Windows)
```

---

## ✅ Verify Setup

Check everything is working:

```bash
# 1. Check Python version (need 3.10+)
python --version

# 2. Check pytest installed
pytest --version

# 3. Run single test
pytest tests/test_email_mcp.py::TestConnection::test_mock_server_starts -v

# Expected output:
# tests/test_email_mcp.py::TestConnection::test_mock_server_starts PASSED [100%]
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r tests/requirements.txt
```

### "No tests found"
```bash
# Check you're in project root
cd /path/to/hackathon0-personal-ai-employee
pytest tests/test_email_mcp.py
```

### "Server failed to start"
```bash
# For integration tests only
cd mcp_servers/email
npm install
node server.js  # Test manually
```

### Tests are slow
```bash
# Run quick tests only
pytest tests/test_email_mcp.py -m "not slow"
```

---

## 📚 Next Steps

1. ✅ **Tests passing?** Great! Move on to integration tests
2. ⬜ **Add new tests?** See `tests/README.md`
3. ⬜ **CI/CD setup?** See `tests/README.md` → CI/CD Integration
4. ⬜ **Coverage low?** See `tests/README.md` → Writing Tests

---

## 🎯 Test Checklist

- [x] Dependencies installed
- [x] Mock tests pass
- [ ] Coverage > 80%
- [ ] Integration tests configured (optional)
- [ ] Integration tests pass (optional)
- [ ] CI/CD configured (optional)

---

## 💡 Pro Tips

1. **Use test runners** for convenience:
   ```bash
   ./tests/run_tests.sh coverage
   ```

2. **Filter by test name**:
   ```bash
   pytest tests/test_email_mcp.py -k "draft"
   ```

3. **Parallel execution** (faster):
   ```bash
   pip install pytest-xdist
   pytest tests/test_email_mcp.py -n auto
   ```

4. **Watch mode** (run on file change):
   ```bash
   ./tests/run_tests.sh watch
   ```

5. **Clean between runs**:
   ```bash
   ./tests/run_tests.sh clean
   ```

---

## 🎉 Success!

If you see:

```
tests/test_email_mcp.py ........................ [100%]

=============== 50 passed in 2.34s ===============
```

**You're all set!** Your test suite is working perfectly.

---

## 📞 Need Help?

- **Full docs:** `tests/README.md`
- **Test code:** `tests/test_email_mcp.py`
- **Configuration:** `tests/.env.test`
- **Pytest docs:** https://docs.pytest.org/

---

**Last Updated:** February 2026
**Estimated Time:** 2 minutes to get started
**Test Count:** 50+ tests
**Coverage Target:** 80%+
