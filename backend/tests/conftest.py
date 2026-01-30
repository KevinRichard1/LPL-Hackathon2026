"""
Pytest configuration and shared fixtures for Audio Transcription Pipeline tests.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any


@pytest.fixture
def mock_lambda_context():
    """Mock AWS Lambda context for testing."""
    context = Mock()
    context.aws_request_id = "test-request-id-123"
    context.function_name = "audio-transcription-pipeline"
    context.function_version = "1.0.0"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:audio-transcription-pipeline"
    context.memory_limit_in_mb = 512
    context.remaining_time_in_millis = lambda: 30000
    return context


@pytest.fixture
def sample_s3_event():
    """Sample S3 event for testing."""
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2024-01-01T12:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "audio-uploads"
                    },
                    "object": {
                        "key": "test-audio.mp3",
                        "size": 1024000
                    }
                }
            }
        ]
    }


@pytest.fixture
def sample_transcribe_job_response():
    """Sample Amazon Transcribe job response for testing."""
    return {
        "TranscriptionJob": {
            "TranscriptionJobName": "test-job-123",
            "TranscriptionJobStatus": "COMPLETED",
            "Media": {
                "MediaFileUri": "s3://audio-uploads/test-audio.mp3"
            },
            "Transcript": {
                "TranscriptFileUri": "s3://transcripts-raw/test-job-123.json"
            }
        }
    }


@pytest.fixture
def sample_transcribe_json_output():
    """Sample Transcribe JSON output for testing."""
    return {
        "jobName": "test-job-123",
        "accountId": "123456789012",
        "results": {
            "transcripts": [
                {
                    "transcript": "This is a sample transcript text for testing purposes."
                }
            ],
            "items": [
                {
                    "start_time": "0.0",
                    "end_time": "1.5",
                    "alternatives": [
                        {
                            "confidence": "0.99",
                            "content": "This"
                        }
                    ],
                    "type": "pronunciation"
                }
            ]
        },
        "status": "COMPLETED"
    }