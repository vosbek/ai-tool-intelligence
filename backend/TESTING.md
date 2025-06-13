# Testing Guide - AI Tool Intelligence Platform

This document provides comprehensive guidance on testing the enhanced AWS strand agent tools and supporting infrastructure.

## 🧪 **Test Framework Overview**

The testing framework uses **PyTest** with comprehensive coverage, mocking, and CI/CD integration.

### **Test Structure**
```
backend/tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # PyTest configuration and fixtures
├── test_free_apis_config.py        # Configuration and rate limiting tests
├── test_enhanced_web_scraper.py    # Web scraping functionality tests
├── test_github_analyzer.py         # GitHub analysis tool tests
├── test_all_tools_integration.py   # Integration tests for all tools
└── [additional test files...]
```

## 🚀 **Quick Start**

### **1. Install Test Dependencies**
```bash
cd backend
pip install -r requirements-test.txt
```

### **2. Run Basic Tests**
```bash
# Run unit tests only (fast)
make test

# Run all tests
make test-all

# Run with coverage
make coverage
```

### **3. Using the Test Runner**
```bash
# Custom test runner with options
python run_tests.py --unit --verbose
python run_tests.py --integration
python run_tests.py --ci  # Full CI pipeline
```

## 📋 **Test Categories**

### **Unit Tests** (`@pytest.mark.unit`)
- **Fast execution** (< 5 seconds total)
- **No external dependencies**
- **Comprehensive mocking**
- **Core logic verification**

```bash
# Run unit tests only
pytest tests/ -m "unit"
make test-unit
```

### **Integration Tests** (`@pytest.mark.integration`) 
- **Multi-component interactions**
- **End-to-end workflows**
- **May require external services**
- **Slower execution**

```bash
# Run integration tests
pytest tests/ -m "integration"
make test-integration
```

### **API Tests** (`@pytest.mark.api`)
- **Require actual API keys**
- **Test real API interactions**
- **Network dependent**

```bash
# Run API tests (requires API keys)
pytest tests/ -m "api"
make test-api
```

### **Performance Tests** (`@pytest.mark.slow`)
- **Performance benchmarks**
- **Memory usage tests**
- **Large dataset processing**

```bash
# Run performance tests
pytest tests/ -m "slow"
make test-slow
```

## 🔧 **Test Configuration**

### **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (for API tests)
nano .env
```

**Required for API Tests:**
- `GITHUB_TOKEN` - GitHub personal access token
- `FIRECRAWL_API_KEY` - Firecrawl API key
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key (optional)
- `NEWS_API_KEY` - News API key (optional)

### **PyTest Configuration** (pytest.ini)
- **Coverage targets**: 80% minimum
- **Test discovery**: Automatic
- **Timeout**: 300 seconds max
- **Parallel execution**: Available with `-n auto`

## 🏗️ **Available Test Commands**

### **Make Commands**
```bash
make help                 # Show all available commands
make install             # Install all dependencies
make test               # Run default unit tests
make test-all           # Run all test categories
make test-fast          # Run fast tests only
make coverage           # Generate coverage report
make coverage-html      # Generate HTML coverage report
make lint               # Run code linting
make format             # Auto-format code
make quality            # Run all quality checks
make ci                 # Run full CI pipeline
make clean              # Clean generated files
```

### **PyTest Direct Commands**
```bash
# Basic test execution
pytest tests/                           # Run all tests
pytest tests/test_github_analyzer.py    # Run specific test file
pytest tests/ -k "test_config"          # Run tests matching pattern

# With markers
pytest tests/ -m "unit"                 # Unit tests only
pytest tests/ -m "not slow"             # Exclude slow tests
pytest tests/ -m "api and github"       # API tests for GitHub

# Coverage and reporting
pytest tests/ --cov=. --cov-report=html
pytest tests/ --tb=short               # Short traceback format
pytest tests/ -v                       # Verbose output
pytest tests/ --durations=10           # Show 10 slowest tests
```

### **Custom Test Runner**
```bash
# Basic usage
python run_tests.py --unit              # Unit tests
python run_tests.py --integration       # Integration tests
python run_tests.py --api              # API tests
python run_tests.py --all              # All tests

# Quality checks
python run_tests.py --lint             # Linting only
python run_tests.py --type-check       # Type checking
python run_tests.py --security         # Security checks
python run_tests.py --quality          # All quality checks

# Options
python run_tests.py --verbose          # Verbose output
python run_tests.py --no-coverage      # Skip coverage
python run_tests.py --report           # Generate test report
python run_tests.py --ci               # Full CI mode
```

## 🧩 **Test Fixtures and Mocking**

### **Key Fixtures** (conftest.py)
- `mock_env_vars`: Mock environment variables
- `sample_github_repo_data`: Sample GitHub repository data
- `sample_pricing_page_content`: Sample pricing page HTML
- `mock_requests_response`: Mock HTTP responses
- `mock_firecrawl_response`: Mock Firecrawl API responses

### **Mocking Strategy**
```python
# Example test with mocking
def test_github_analyzer(mock_env_vars, mock_requests_response, sample_github_repo_data):
    with patch('enhanced_strands_tools.requests.get') as mock_get:
        mock_get.return_value = mock_requests_response(200, sample_github_repo_data)
        
        result = enhanced_github_analyzer("https://github.com/user/repo")
        
        assert "error" not in result
        assert result["basic_stats"]["stars"] == 1500
```

## 📊 **Coverage Reporting**

### **Generate Coverage Reports**
```bash
# Terminal coverage report
make coverage

# HTML coverage report
make coverage-html
open htmlcov/index.html

# Serve coverage report
make coverage-serve  # Available at http://localhost:8000
```

### **Coverage Targets**
- **Minimum**: 80% overall coverage
- **Goal**: 90%+ for critical components
- **Exclusions**: Test files, external dependencies

## 🔄 **Continuous Integration**

### **GitHub Actions Workflow**
The `.github/workflows/test.yml` provides:

- **Multi-Python versions** (3.9, 3.10, 3.11)
- **Automated testing** on push/PR
- **Quality checks** (linting, type checking, security)
- **Coverage reporting** to Codecov
- **Docker testing** environment
- **Performance monitoring**

### **CI Test Categories**
```yaml
# Standard CI pipeline
- Linting (flake8)
- Type checking (mypy)
- Security checks (bandit)
- Unit tests (pytest with coverage)
- Integration tests (if API keys available)
```

### **Local CI Simulation**
```bash
# Run full CI pipeline locally
make ci
python run_tests.py --ci
```

## 🐛 **Debugging Tests**

### **Common Issues**

**1. Import Errors**
```bash
# Ensure backend directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**2. API Rate Limits**
```bash
# Use unit tests to avoid API calls
pytest tests/ -m "unit"
```

**3. Network Issues**
```bash
# Skip network-dependent tests
pytest tests/ -m "not network"
```

### **Debugging Commands**
```bash
# Run single test with detailed output
pytest tests/test_github_analyzer.py::TestEnhancedGitHubAnalyzer::test_github_analyzer_success -v -s

# Debug test failures
pytest tests/ --tb=long                 # Long traceback
pytest tests/ --pdb                     # Drop into debugger on failure
pytest tests/ --lf                      # Run last failed tests only
```

## 📈 **Performance Testing**

### **Benchmark Tests**
```bash
# Run performance benchmarks
make benchmark
pytest tests/ -m "slow" --benchmark-only
```

### **Memory Usage Testing**
```bash
# Monitor memory usage during tests
python -c "
import psutil
import os
print(f'Memory before tests: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.2f} MB')
"
```

## 🔒 **Security Testing**

### **Security Checks**
```bash
# Run security audit
make security
bandit -r . -x tests/

# Check for vulnerabilities in dependencies
safety check -r requirements.txt
```

## 📝 **Writing New Tests**

### **Test Naming Convention**
```python
# File naming: test_[module_name].py
# Class naming: Test[ComponentName]
# Method naming: test_[specific_behavior]

class TestEnhancedWebScraper:
    def test_scrape_url_success(self):
        """Test successful URL scraping"""
        pass
    
    def test_scrape_url_with_invalid_url(self):
        """Test scraping with invalid URL"""
        pass
```

### **Test Structure Template**
```python
import pytest
from unittest.mock import patch, Mock

@pytest.mark.unit
class TestNewComponent:
    """Test suite for new component"""
    
    def test_basic_functionality(self, mock_env_vars):
        """Test basic functionality works as expected"""
        # Arrange
        # Act  
        # Assert
        pass
    
    def test_error_handling(self):
        """Test component handles errors gracefully"""
        pass
    
    @pytest.mark.slow
    def test_performance(self):
        """Test performance characteristics"""
        pass
```

### **Adding Test Fixtures**
```python
# In conftest.py
@pytest.fixture
def sample_new_data():
    """Sample data for new component testing"""
    return {
        "field1": "value1",
        "field2": "value2"
    }
```

## 🎯 **Best Practices**

### **Test Design**
1. **Arrange-Act-Assert** pattern
2. **Single responsibility** per test
3. **Descriptive test names**
4. **Independent tests** (no interdependencies)
5. **Fast execution** for unit tests

### **Mocking Guidelines**
1. **Mock external dependencies** (APIs, file system, network)
2. **Use realistic test data**
3. **Verify mock interactions** when relevant
4. **Keep mocks simple** and focused

### **Coverage Goals**
1. **Test happy paths** and error conditions
2. **Cover edge cases** and boundary conditions
3. **Test configuration variations**
4. **Verify error handling** and recovery

## 🚨 **Troubleshooting**

### **Common Test Failures**

**Configuration Issues:**
```bash
# Check environment setup
python -c "from config.free_apis_config import FreeAPIConfig; print(FreeAPIConfig.validate_config())"
```

**Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"
```

**Rate Limiting:**
```bash
# Clear rate limiting cache
python -c "from config.free_apis_config import FreeAPIConfig; FreeAPIConfig._rate_limit_storage.clear()"
```

### **Getting Help**
1. Check test output and error messages
2. Review this documentation
3. Run tests with verbose output (`-v`)
4. Use debugging mode (`--pdb`)
5. Check CI logs for additional context

---

## 📞 **Support**

For testing-related issues:
1. Check the troubleshooting section above
2. Review test logs and error messages  
3. Ensure all dependencies are installed
4. Verify environment configuration

**Happy Testing! 🧪✨**