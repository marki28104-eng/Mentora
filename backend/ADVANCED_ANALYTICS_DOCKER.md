# Advanced Analytics Docker Setup

This document describes how to run the advanced analytics features in Docker.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available memory for ML operations
- MySQL database (can be containerized)

## Docker Configuration

### Updated Dependencies

The `requirements.txt` has been updated to include ML dependencies:

```
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
httpx>=0.24.0
joblib>=1.3.0
```

### Dockerfile Updates

The Dockerfile has been updated to include system dependencies for ML packages:

- Build stage: Added `gcc`, `g++`, `libc6-dev`, `libffi-dev`, `libssl-dev`
- Runtime stage: Added `libgomp1`, `libopenblas-dev`, `liblapack-dev`, `libblas-dev`, `gfortran`

### Environment Variables

Configure the following environment variables for advanced analytics:

```bash
# Advanced Analytics Configuration
ANALYTICS_MODEL_RETRAIN_INTERVAL_HOURS=24
ANALYTICS_SESSION_CLEANUP_INTERVAL_HOURS=24
ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING=50
ANALYTICS_ENABLE_REAL_TIME_PERSONALIZATION=true
ANALYTICS_ENABLE_PREDICTIVE_MODELS=true
ANALYTICS_ENABLE_COHORT_ANALYSIS=true

# Umami Analytics (optional)
UMAMI_API_URL=https://your-umami-instance.com
UMAMI_API_TOKEN=your-api-token
UMAMI_WEBSITE_ID=your-website-id
```

## Running with Docker Compose

### Basic Setup

```bash
# Build and run the application
docker-compose up --build
```

### With Analytics Configuration

Use the provided analytics override file:

```bash
# Run with analytics-specific configuration
docker-compose -f docker-compose.yml -f docker-compose.analytics.yml up --build
```

### Memory Configuration

The analytics features require additional memory for ML operations. The `docker-compose.analytics.yml` file includes:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

## Testing the Setup

### 1. Test ML Dependencies

Run the ML dependencies test:

```bash
docker run --rm your-backend-image python test_ml_dependencies.py
```

### 2. Test Docker Build

Use the provided test script:

```bash
./test_docker_build.sh
```

### 3. Test Analytics Endpoints

Once the application is running, test the analytics endpoints:

```bash
# Check analytics status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/advanced-analytics/analytics-status

# Get available cohort types
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/advanced-analytics/cohort-types
```

## API Endpoints

The advanced analytics features provide the following endpoints:

- `POST /advanced-analytics/initialize` - Initialize ML models (admin only)
- `GET /advanced-analytics/predict-outcome/{course_id}` - Get learning outcome prediction
- `GET /advanced-analytics/cohort-analysis` - Get cohort analysis (admin only)
- `POST /advanced-analytics/real-time-event` - Process real-time learning events
- `GET /advanced-analytics/analytics-status` - Get system status
- `GET /advanced-analytics/cohort-types` - Get available cohort types
- `POST /advanced-analytics/cleanup-sessions` - Clean up old session data (admin only)

## Performance Considerations

### Memory Usage

- ML models require significant memory during training
- Real-time personalization keeps session data in memory
- Consider using Redis for session storage in production

### CPU Usage

- Model training is CPU-intensive
- Consider running training jobs during off-peak hours
- Use background tasks for model retraining

### Storage

- Analytics data grows over time
- Implement data retention policies
- Consider data archiving for old analytics data

## Monitoring

### Health Checks

The analytics service includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/advanced-analytics/analytics-status"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logging

Analytics operations are logged with appropriate levels:

- INFO: Normal operations, model training completion
- WARNING: Insufficient data, configuration issues
- ERROR: Model training failures, API errors

### Metrics

Monitor the following metrics:

- Model training success/failure rates
- Prediction accuracy over time
- Real-time personalization trigger rates
- Memory and CPU usage during ML operations

## Troubleshooting

### Common Issues

1. **Out of Memory Errors**
   - Increase Docker memory limits
   - Reduce batch sizes for model training
   - Enable swap if necessary

2. **ML Package Import Errors**
   - Verify system dependencies are installed
   - Check Python version compatibility
   - Run the ML dependencies test

3. **Model Training Failures**
   - Check data quality and quantity
   - Verify database connectivity
   - Review training data preparation logic

4. **Real-time Personalization Not Working**
   - Verify configuration is enabled
   - Check session data storage
   - Review event data format

### Debug Mode

Enable debug logging for analytics:

```bash
export ANALYTICS_DEBUG=true
```

This will provide detailed logging for troubleshooting.

## Production Deployment

### Scaling Considerations

- Use separate containers for ML training and API serving
- Consider using a job queue for model training
- Implement horizontal scaling for API endpoints

### Security

- Ensure analytics endpoints require proper authentication
- Sanitize all user input data
- Implement rate limiting for expensive operations

### Data Privacy

- The system automatically filters PII from analytics data
- Implement data retention policies
- Provide user data deletion capabilities

## Development

### Local Development

For local development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run ML dependencies test
python test_ml_dependencies.py

# Start the application
uvicorn src.main:app --reload
```

### Testing

Run the analytics tests:

```bash
# Unit tests
pytest test/test_advanced_analytics_service.py -v

# API tests
pytest test/test_advanced_analytics_api.py -v
```