"""
Unit tests for S3 event parser module.

Tests cover S3 event JSON parsing, metadata extraction, and error handling
for various event structures and edge cases.
"""

import pytest
from datetime import datetime
from audio_transcription.s3_event_parser import S3EventParser, S3EventRecord


class TestS3EventParser:
    """Test cases for S3EventParser class."""
    
    def test_parse_single_record_event(self):
        """Test parsing S3 event with single record."""
        event = {
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
                            "key": "meeting.mp3",
                            "size": 1024000
                        }
                    }
                }
            ]
        }
        
        records = S3EventParser.parse_s3_event(event)
        
        assert len(records) == 1
        record = records[0]
        assert record.bucket_name == "audio-uploads"
        assert record.object_key == "meeting.mp3"
        assert record.event_name == "ObjectCreated:Put"
        assert record.object_size == 1024000
        assert record.event_version == "2.1"
        assert record.aws_region == "us-east-1"
        assert isinstance(record.event_time, datetime)
    
    def test_parse_multiple_records_event(self):
        """Test parsing S3 event with multiple records."""
        event = {
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
                            "key": "meeting.mp3",
                            "size": 1024000
                        }
                    }
                },
                {
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "us-west-2",
                    "eventTime": "2024-01-01T12:05:00.000Z",
                    "eventName": "ObjectCreated:Post",
                    "s3": {
                        "bucket": {
                            "name": "audio-uploads"
                        },
                        "object": {
                            "key": "interview.wav",
                            "size": 2048000
                        }
                    }
                }
            ]
        }
        
        records = S3EventParser.parse_s3_event(event)
        
        assert len(records) == 2
        assert records[0].object_key == "meeting.mp3"
        assert records[1].object_key == "interview.wav"
        assert records[0].aws_region == "us-east-1"
        assert records[1].aws_region == "us-west-2"
    
    def test_parse_event_with_optional_fields_missing(self):
        """Test parsing event with optional fields missing."""
        event = {
            "Records": [
                {
                    "eventTime": "2024-01-01T12:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": "audio-uploads"
                        },
                        "object": {
                            "key": "meeting.mp3"
                        }
                    }
                }
            ]
        }
        
        records = S3EventParser.parse_s3_event(event)
        
        assert len(records) == 1
        record = records[0]
        assert record.bucket_name == "audio-uploads"
        assert record.object_key == "meeting.mp3"
        assert record.object_size is None
        assert record.event_version is None
        assert record.aws_region is None
    
    def test_extract_bucket_name(self):
        """Test extracting bucket name from event."""
        event = {
            "Records": [
                {
                    "eventTime": "2024-01-01T12:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        },
                        "object": {
                            "key": "file.mp3"
                        }
                    }
                }
            ]
        }
        
        bucket_name = S3EventParser.extract_bucket_name(event)
        assert bucket_name == "test-bucket"
    
    def test_extract_object_keys(self):
        """Test extracting all object keys from event."""
        event = {
            "Records": [
                {
                    "eventTime": "2024-01-01T12:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": "audio-uploads"
                        },
                        "object": {
                            "key": "file1.mp3"
                        }
                    }
                },
                {
                    "eventTime": "2024-01-01T12:05:00.000Z",
                    "eventName": "ObjectCreated:Post",
                    "s3": {
                        "bucket": {
                            "name": "audio-uploads"
                        },
                        "object": {
                            "key": "file2.wav"
                        }
                    }
                }
            ]
        }
        
        object_keys = S3EventParser.extract_object_keys(event)
        assert object_keys == ["file1.mp3", "file2.wav"]
    
    def test_filter_create_events(self):
        """Test filtering records to include only creation events."""
        records = [
            S3EventRecord(
                bucket_name="test-bucket",
                object_key="file1.mp3",
                event_name="ObjectCreated:Put",
                event_time=datetime.now()
            ),
            S3EventRecord(
                bucket_name="test-bucket",
                object_key="file2.mp3",
                event_name="ObjectRemoved:Delete",
                event_time=datetime.now()
            ),
            S3EventRecord(
                bucket_name="test-bucket",
                object_key="file3.wav",
                event_name="s3:ObjectCreated:Post",
                event_time=datetime.now()
            )
        ]
        
        create_records = S3EventParser.filter_create_events(records)
        
        assert len(create_records) == 2
        assert create_records[0].object_key == "file1.mp3"
        assert create_records[1].object_key == "file3.wav"


class TestS3EventParserErrorHandling:
    """Test error handling in S3EventParser."""
    
    def test_invalid_event_type(self):
        """Test error handling for non-dictionary event."""
        with pytest.raises(ValueError, match="Event must be a dictionary"):
            S3EventParser.parse_s3_event("invalid")
    
    def test_missing_records_field(self):
        """Test error handling for missing Records field."""
        event = {"NotRecords": []}
        with pytest.raises(ValueError, match="Event must contain 'Records' field"):
            S3EventParser.parse_s3_event(event)
    
    def test_invalid_records_type(self):
        """Test error handling for non-list Records field."""
        event = {"Records": "invalid"}
        with pytest.raises(ValueError, match="Records must be a list"):
            S3EventParser.parse_s3_event(event)
    
    def test_missing_required_fields(self):
        """Test error handling for missing required fields in record."""
        event = {
            "Records": [
                {
                    "eventTime": "2024-01-01T12:00:00.000Z",
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        }
                        # Missing object field
                    }
                }
            ]
        }
        
        with pytest.raises(ValueError, match="Invalid record structure"):
            S3EventParser.parse_s3_event(event)
    
    def test_empty_bucket_name(self):
        """Test error handling for empty bucket name."""
        event = {
            "Records": [
                {
                    "eventTime": "2024-01-01T12:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": ""
                        },
                        "object": {
                            "key": "file.mp3"
                        }
                    }
                }
            ]
        }
        
        with pytest.raises(ValueError, match="Invalid record structure"):
            S3EventParser.parse_s3_event(event)
    
    def test_invalid_event_time_format(self):
        """Test error handling for invalid event time format."""
        event = {
            "Records": [
                {
                    "eventTime": "invalid-time",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        },
                        "object": {
                            "key": "file.mp3"
                        }
                    }
                }
            ]
        }
        
        with pytest.raises(ValueError, match="Invalid record structure"):
            S3EventParser.parse_s3_event(event)
    
    def test_extract_bucket_name_no_records(self):
        """Test error handling when extracting bucket name from empty event."""
        event = {"Records": []}
        
        with pytest.raises(ValueError, match="No records found in event"):
            S3EventParser.extract_bucket_name(event)