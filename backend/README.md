# Audio Transcription Pipeline

A serverless AWS Lambda-based system for automatically transcribing audio files uploaded to S3 using Amazon Transcribe service.

## Project Structure

```
backend/
├── audio_transcription/          # Main package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── logging_config.py        # Structured logging setup
│   └── lambda_handler.py        # Main Lambda handler
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_config.py          # Configuration tests
│   ├── test_logging_config.py  # Logging tests
│   └── test_lambda_handler.py  # Lambda handler tests
├── requirements.txt             # Python dependencies
├── setup.py                    # Package setup
├── pytest.ini                 # Pytest configuration
└── README.md                   # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

The system uses environment variables for configuration:

- `AUDIO_UPLOAD_BUCKET`: S3 bucket for audio uploads (default: "audio-uploads")
- `TRANSCRIPT_STORAGE_BUCKET`: S3 bucket for transcripts (default: "transcripts-raw")
- `AWS_REGION`: AWS region (default: "us-east-1")
- `TRANSCRIBE_LANGUAGE_CODE`: Language for transcription (default: "en-US")
- `LOG_LEVEL`: Logging level (default: "INFO")

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=audio_transcription

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m property
```

## Logging

The system uses structured JSON logging compatible with AWS CloudWatch. All logs include:

- Timestamp in ISO format
- Log level and logger name
- Service and version information
- Contextual information for debugging

## AWS Permissions

The Lambda function requires the following IAM permissions:

- `s3:GetObject` on the audio upload bucket
- `s3:PutObject` on the transcript storage bucket
- `transcribe:StartTranscriptionJob`
- `transcribe:GetTranscriptionJob`
- CloudWatch Logs permissions for logging

## Development

This project follows the spec-driven development methodology with:

- Requirements-based design
- Property-based testing using Hypothesis
- Comprehensive unit and integration tests
- Structured logging for observability