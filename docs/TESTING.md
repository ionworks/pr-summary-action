# Testing Guide for PR Summary Action

This document provides comprehensive information about testing the PR Summary Action with realistic scenarios.

## Test Structure

The testing framework is organized into several components:

```
tests/
├── __init__.py                 # Test package initialization
├── test_credentials.py         # Basic credential validation tests
├── test_fixtures.py           # Mock data for realistic scenarios
├── test_summarize.py          # Unit tests for core functionality
├── test_integration.py        # Integration tests with full workflows
└── test_config.py             # Configuration management tests
```

## Test Categories

### 1. Unit Tests (`test_summarize.py`)

Tests individual functions in isolation:

- `TestLoadPRData` - Loading and parsing GitHub event data
- `TestShouldProcessPR` - PR processing logic
- `TestGetPRDiff` - GitHub API diff retrieval
- `TestGenerateSummaries` - OpenAI summary generation
- `TestPostToSlack` - Slack message posting
- `TestMain` - Main function orchestration

### 2. Integration Tests (`test_integration.py`)

Tests complete workflows:

- `TestFullWorkflowIntegration` - End-to-end scenarios
- `TestErrorHandlingIntegration` - Error recovery testing
- `TestRealWorldScenarios` - Realistic usage patterns

### 3. Configuration Tests (`test_config.py`)

Tests configuration management:

- Environment variable parsing
- Configuration validation
- Error handling for invalid configurations
- Boundary value testing

### 4. Credential Tests (`test_credentials.py`)

Tests external service connectivity:

- OpenAI API key validation
- Slack webhook validation
- Live API connectivity (marked as integration tests)

## Mock Data and Fixtures

### GitHub Event Types

The test fixtures include realistic GitHub events for:

#### Feature PRs

- OAuth2 authentication implementation
- Comprehensive PR description with security notes
- Multiple labels and milestone assignment
- Proper author and merge information

#### Bugfix PRs

- Memory leak fixes
- Critical bug labels
- Reproduction steps and testing notes
- Performance improvements

#### Documentation PRs

- API documentation updates
- Technical writing improvements
- Screenshot updates
- Typo fixes and formatting

#### Refactoring PRs

- Code architecture improvements
- Performance optimizations
- Better error handling
- Test coverage improvements

### PR Diffs

Realistic code diffs for each PR type:

- **Feature diffs**: New file creation, API additions
- **Bugfix diffs**: Code fixes, memory management
- **Documentation diffs**: Markdown updates, examples
- **Refactor diffs**: Code restructuring, interfaces

### OpenAI Responses

Mock OpenAI responses for different scenarios:

- Valid JSON responses with technical and marketing summaries
- Invalid JSON responses for error testing
- Empty responses for edge case handling
- Model-specific response variations

## Running Tests

### All Tests

```bash
pytest tests/
```

### Unit Tests Only

```bash
pytest tests/test_summarize.py
```

### Integration Tests Only

```bash
pytest tests/test_integration.py
```

### Configuration Tests

```bash
pytest tests/test_config.py
```

### Skip Integration Tests

```bash
pytest tests/ -m "not integration"
```

### Run with Coverage

```bash
pytest tests/ --cov=src/pr_summary_action --cov-report=html
```

## Test Scenarios

### 1. Happy Path Testing

**Feature PR Workflow:**

1. GitHub event with merged feature PR
2. GitHub API returns realistic diff
3. OpenAI generates proper summaries
4. Slack receives formatted message with author info

**Expected Slack Message:**

```
🚀 PR #42 Merged: Add user authentication with OAuth2

PR #42: Add user authentication with OAuth2
Author: John Developer (@developer1)
Merged by: Jane Maintainer (@maintainer1)
Branches: feature/oauth2-auth → main

Technical: Added OAuth2 authentication support with Google provider...
Marketing: Users can now securely log in using their Google accounts...

[View PR Button]
```

### 2. Error Handling Testing

**OpenAI JSON Parsing Errors:**

- Invalid JSON responses
- Empty responses
- Malformed JSON structures
- Network timeouts

**GitHub API Errors:**

- Authentication failures
- Rate limiting
- Network connectivity issues
- Invalid repository access

**Slack API Errors:**

- Invalid webhook URLs
- Network failures
- Message formatting errors
- Rate limiting

### 3. Edge Cases

**Large PRs:**

- Diffs exceeding max length (automatically truncated)
- Multiple file changes
- Complex merge scenarios

**Minimal PRs:**

- Empty descriptions
- Single-line changes
- Documentation-only changes

**Configuration Variations:**

- Different OpenAI models (GPT-3.5, GPT-4)
- Various temperature and token settings
- Debug mode on/off
- Custom diff lengths

## Realistic Test Data

### PR Descriptions

Test data includes realistic PR descriptions with:

- **Security considerations**
- **Testing instructions**
- **Migration notes**
- **Performance impact**
- **Review checklist items**

### Code Changes

Mock diffs include:

- **Authentication systems**
- **Database migrations**
- **API endpoints**
- **UI components**
- **Configuration files**

### Author Information

Test data includes various author types:

- **Individual developers**
- **Technical writers**
- **DevOps engineers**
- **External contributors**

## Custom Test Scenarios

### Creating New Test Cases

1. **Add to fixtures** (`test_fixtures.py`):

```python
@staticmethod
def custom_pr_event() -> Dict[str, Any]:
    # Create custom PR event data
    pass
```

2. **Create test method**:

```python
def test_custom_scenario(self):
    # Test your specific scenario
    pass
```

3. **Add realistic diffs**:

```python
@staticmethod
def custom_diff() -> str:
    # Return realistic diff content
    pass
```

### Testing Different PR Types

The framework supports testing:

- **Hotfix PRs** - Critical production fixes
- **Dependencies** - Package updates
- **Security** - Vulnerability fixes
- **Performance** - Optimization changes
- **CI/CD** - Pipeline improvements

## Performance Testing

### Load Testing

```bash
pytest tests/test_integration.py::TestRealWorldScenarios::test_large_pr_with_multiple_files
```

### Memory Testing

```bash
pytest tests/ --profile
```

### Concurrency Testing

```bash
pytest tests/ -n auto
```

## Configuration Testing

### Environment Variables

Test various configuration scenarios:

```bash
# Test with GPT-4
export MODEL=gpt-4
pytest tests/test_integration.py

# Test with debugging disabled
export ENABLE_DEBUG=false
pytest tests/

# Test with custom parameters
export MAX_TOKENS=1000
export TEMPERATURE=0.8
pytest tests/
```

### Validation Testing

Configuration validation covers:

- **Required fields** - Missing environment variables
- **Valid ranges** - Token limits, temperature bounds
- **Format validation** - Webhook URLs, API keys
- **Model validation** - Supported OpenAI models

## Debugging Test Failures

### Common Issues

1. **Import errors** - Check Python path
2. **Mock failures** - Verify mock setup
3. **Configuration errors** - Check environment variables
4. **Network timeouts** - Increase timeout values

### Debug Mode

Enable debug logging in tests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Pytest Debugging

```bash
# Run with verbose output
pytest tests/ -v

# Run with debug output
pytest tests/ -s

# Run specific test with debugging
pytest tests/test_integration.py::TestFullWorkflowIntegration::test_feature_pr_complete_workflow -v -s
```

## Continuous Integration

### GitHub Actions Testing

The test suite is designed to run in CI/CD:

```yaml
- name: Run tests
  run: |
    pytest tests/ --cov=src/pr_summary_action
    pytest tests/ -m "not integration"  # Skip integration tests in CI
```

### Test Data Management

- **Mock data** - No external dependencies
- **Deterministic** - Consistent test results
- **Fast execution** - Under 30 seconds for full suite
- **Isolated** - No test interference

## Contributing Tests

When adding new features:

1. **Add unit tests** for individual functions
2. **Add integration tests** for complete workflows
3. **Add realistic fixtures** for new scenarios
4. **Update documentation** with test instructions
5. **Ensure coverage** meets project standards

### Test Quality Guidelines

- **Clear test names** - Describe what's being tested
- **Realistic data** - Use production-like scenarios
- **Proper mocking** - Mock external dependencies
- **Error scenarios** - Test failure conditions
- **Edge cases** - Test boundary conditions

## Maintenance

### Updating Test Data

When GitHub API changes:

1. Update `test_fixtures.py` with new event structures
2. Update mock responses in integration tests
3. Verify all tests still pass
4. Update documentation if needed

### Keeping Tests Current

- **Regular updates** - Monthly test data review
- **API changes** - Monitor OpenAI and GitHub API updates
- **Dependency updates** - Keep test dependencies current
- **Performance monitoring** - Track test execution times
