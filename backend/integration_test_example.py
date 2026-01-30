#!/usr/bin/env python3
"""
Integration test example for the Audio Transcription Pipeline Lambda handler.

This script demonstrates how the Lambda handler processes S3 events for both
audio files and transcription results.
"""

import json
from datetime import datetime, timezone
from audio_transcription.lambda_handler import lambda_handler


def create_sample_s3_audio_event():
    """Create a sample S3 event for an audio file upload."""
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "audio-uploads"
                    },
                    "object": {
                        "key": "meeting-recording.mp3",
                        "size": 1024000
                    }
                }
            }
        ]
    }


def create_sample_s3_transcription_result_event():
    """Create a sample S3 event for a transcription result JSON file."""
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "transcripts-raw"
                    },
                    "object": {
                        "key": "transcribe-meeting-recording-20240130-123456-abc123.json",
                        "size": 2048
                    }
                }
            }
        ]
    }


class MockLambdaContext:
    """Mock AWS Lambda context for testing."""
    
    def __init__(self):
        self.aws_request_id = "test-request-id-123"
        self.function_name = "audio-transcription-pipeline"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:audio-transcription-pipeline"
        self.memory_limit_in_mb = 512
        self.remaining_time_in_millis = 30000


def main():
    """Run integration test examples."""
    print("Audio Transcription Pipeline - Integration Test Examples")
    print("=" * 60)
    
    # Create mock context
    context = MockLambdaContext()
    
    # Test 1: Audio file upload event
    print("\n1. Testing audio file upload event:")
    print("-" * 40)
    
    audio_event = create_sample_s3_audio_event()
    print(f"Input event: {json.dumps(audio_event, indent=2)}")
    
    try:
        # Note: This will fail in actual execution because AWS services aren't available
        # But it demonstrates the event structure and handler interface
        result = lambda_handler(audio_event, context)
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Expected error (AWS services not available): {e}")
    
    # Test 2: Transcription result event
    print("\n2. Testing transcription result event:")
    print("-" * 40)
    
    transcription_event = create_sample_s3_transcription_result_event()
    print(f"Input event: {json.dumps(transcription_event, indent=2)}")
    
    try:
        # Note: This will also fail because AWS services aren't available
        result = lambda_handler(transcription_event, context)
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Expected error (AWS services not available): {e}")
    
    print("\n" + "=" * 60)
    print("Integration test examples completed.")
    print("\nNote: These examples show the event structure and handler interface.")
    print("In a real AWS environment with proper IAM permissions and S3 buckets,")
    print("the handler would successfully process the events and start transcription jobs.")


if __name__ == "__main__":
    main()