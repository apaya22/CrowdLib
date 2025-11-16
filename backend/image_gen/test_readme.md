# Image Generation App - Test Suite

This directory contains comprehensive tests for the image generation application.

Notice: This file was made primarily with AI

## Test Structure

The test suite is organized into four main test classes:

### 1. `ImageGenerationModelTest`
Tests the core image generation model (`ImageGenerationModel`):
- ✅ Successful image generation
- ✅ Image generation with custom style arguments
- ✅ Handling of empty API responses
- ✅ API exception handling
- ✅ Configuration building (default and custom)
- ✅ Prompt building with and without extras

### 2. `UtilsTest`
Tests utility functions for S3 upload:
- ✅ Successful S3 upload
- ✅ S3 upload failure handling

### 3. `ImageGenerationViewSetTest`
Tests the API endpoints (view layer):

#### Generate Endpoint (`/api/image-gen/generate/`)
- ✅ Successful image generation
- ✅ Missing required fields validation
- ✅ Empty text validation
- ✅ Generation failure handling
- ✅ Invalid madlib ID handling
- ✅ Authentication requirement

#### Upload Endpoint (`/api/image-gen/upload/`)
- ✅ Successful image upload
- ✅ Missing madlib_id validation
- ✅ Missing image file validation
- ✅ Upload failure handling
- ✅ Authentication requirement

### 4. `MadlibModelUpdateImageUrlTest`
Tests the model method for updating image URLs:
- ✅ Successful URL update
- ✅ Non-existent madlib handling
- ✅ Same URL update (idempotency)
- ✅ Invalid ID format handling

## Running the Tests

### Run all image_gen tests:
```bash
python manage.py test image_gen
```

### Run a specific test class:
```bash
python manage.py test image_gen.tests.ImageGenerationModelTest
```

### Run a specific test method:
```bash
python manage.py test image_gen.tests.ImageGenerationModelTest.test_create_image_success
```

### Run with verbose output:
```bash
python manage.py test image_gen --verbosity=2
```

### Run with coverage:
```bash
coverage run --source='image_gen' manage.py test image_gen
coverage report
coverage html  # Generate HTML coverage report
```

## Test Dependencies

The test suite requires the following Python packages:
- `django` - Django framework
- `djangorestframework` - REST framework for API testing
- `pillow` - Image processing for test fixtures
- `pymongo` / `bson` - MongoDB interactions
- `unittest.mock` - Mocking external dependencies

## Mocking Strategy

The tests use extensive mocking to avoid external dependencies:

1. **Gemini API**: Mocked using `unittest.mock.patch` on `genai.Client`
2. **S3 Upload**: Mocked using `unittest.mock.patch` on S3 operations
3. **MongoDB**: Uses actual test database (cleaned up in `tearDown`)

## Key Testing Patterns

### 1. Setup and Teardown
Each test class uses `setUp()` and `tearDown()` methods to:
- Create necessary test data (users, templates, madlibs)
- Clean up after tests to avoid database pollution

### 2. Mocking External Services
```python
@patch('image_gen.models.genai.Client')
def test_create_image_success(self, mock_client_class):
    # Mock implementation
    ...
```

### 3. API Testing with Authentication
```python
self.client.force_authenticate(user=self.user)
response = self.client.post('/api/image-gen/generate/', data, format='json')
```

## Test Coverage

The test suite provides comprehensive coverage of:
- ✅ Happy path scenarios
- ✅ Error handling and edge cases
- ✅ Input validation
- ✅ Authentication and authorization
- ✅ Database operations
- ✅ External API interactions
- ✅ File upload handling

## Common Test Failures and Solutions

### MongoDB Connection Errors
**Problem**: Tests fail with connection errors
**Solution**: Ensure MongoDB is running and accessible
```bash
# Check MongoDB status
brew services list | grep mongodb
# Start MongoDB if needed
brew services start mongodb-community
```

### Import Errors
**Problem**: `ImportError: No module named 'image_gen'`
**Solution**: Ensure you're running tests from the project root
```bash
cd /path/to/CrowdLib/backend
python manage.py test image_gen
```

### Authentication Failures
**Problem**: Tests fail with 401 Unauthorized
**Solution**: Check that `force_authenticate` is called in `setUp()`

### Database Cleanup Issues
**Problem**: Tests fail on subsequent runs
**Solution**: Verify `tearDown()` is properly cleaning up test data

## Writing New Tests

When adding new tests, follow these guidelines:

1. **Use descriptive test names**: `test_<action>_<expected_result>`
2. **Mock external dependencies**: Don't make real API calls or S3 uploads
3. **Clean up test data**: Always implement proper tearDown
4. **Test both success and failure**: Cover happy path and edge cases
5. **Use appropriate assertions**: Choose the right assertion method
6. **Document complex tests**: Add comments explaining non-obvious logic

### Example Test Template
```python
def test_new_feature_success(self):
    """Test successful execution of new feature"""
    # Arrange
    test_data = {...}

    # Act
    result = perform_action(test_data)

    # Assert
    self.assertEqual(result, expected_value)
    self.assertTrue(condition)
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
- name: Run tests
  run: |
    python manage.py test image_gen --verbosity=2
```

## Performance Considerations

- Tests use mocking to avoid slow external API calls
- Database operations use MongoDB test database
- Image file uploads use in-memory BytesIO objects
- Each test class is independent and can run in parallel

## Troubleshooting

### Slow Tests
If tests are running slowly:
1. Verify external services are properly mocked
2. Check MongoDB index performance
3. Use `--parallel` flag for parallel execution

### Flaky Tests
If tests pass/fail intermittently:
1. Check for race conditions in async operations
2. Verify proper cleanup in tearDown
3. Ensure tests don't depend on execution order
