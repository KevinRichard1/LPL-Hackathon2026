"""
Tests for the logging configuration module.
"""

import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest
import structlog

from audio_transcription.logging_config import (
    CloudWatchJSONFormatter,
    setup_logging,
    get_logger,
    log_s3_event,
    log_transcribe_job,
    log_transcribe_completion,
    log_error
)


class TestCloudWatchJSONFormatter:
    """Test cases for CloudWatchJSONFormatter."""
    
    def test_format_basic_log_record(self):
        """Test formatting a basic log record."""
        formatter = CloudWatchJSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["line"] == 42
        assert "timestamp" in log_data
    
    def test_format_log_record_with_exception(self):
        """Test formatting a log record with exception information."""
        formatter = CloudWatchJSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=True
            )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Error occurred"
        assert "exception" in log_data
        assert "ValueError: Test exception" in log_data["exception"]


class TestLoggingSetup:
    """Test cases for logging setup functions."""
    
    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a structlog logger."""
        logger = setup_logging()
        assert isinstance(logger, structlog.BoundLogger)
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a structlog logger."""
        logger = get_logger()
        assert isinstance(logger, structlog.BoundLogger)
    
    def test_get_logger_with_name(self):
        """Test that get_logger accepts a name parameter."""
        logger = get_logger("test_logger")
        assert isinstance(logger, structlog.BoundLogger)


class TestLoggingHelpers:
    """Test cases for logging helper functions."""
    
    @patch('structlog.get_logger')
    def test_log_s3_event(self, mock_get_logger):
        """Test S3 event logging helper."""
        mock_logger = mock_get_logger.return_value
        
        log_s3_event(mock_logger, "test-bucket", "test-key.mp3", "ObjectCreated:Put")
        
        mock_logger.info.assert_called_once_with(
            "S3 event received",
            bucket="test-bucket",
            object_key="test-key.mp3",
            event_name="ObjectCreated:Put",
            event_type="s3_event"
        )
    
    @patch('structlog.get_logger')
    def test_log_transcribe_job(self, mock_get_logger):
        """Test transcribe job logging helper."""
        mock_logger = mock_get_logger.return_value
        
        log_transcribe_job(
            mock_logger,
            "test-job-123",
            "s3://audio-uploads/test.mp3",
            "transcripts-raw"
        )
        
        mock_logger.info.assert_called_once_with(
            "Transcription job created",
            job_name="test-job-123",
            input_uri="s3://audio-uploads/test.mp3",
            output_bucket="transcripts-raw",
            event_type="transcribe_job_created"
        )
    
    @patch('structlog.get_logger')
    def test_log_transcribe_completion(self, mock_get_logger):
        """Test transcribe completion logging helper."""
        mock_logger = mock_get_logger.return_value
        
        log_transcribe_completion(
            mock_logger,
            "test-job-123",
            "COMPLETED",
            "s3://transcripts-raw/test-job-123.json"
        )
        
        mock_logger.info.assert_called_once_with(
            "Transcription job completed",
            job_name="test-job-123",
            status="COMPLETED",
            output_location="s3://transcripts-raw/test-job-123.json",
            event_type="transcribe_job_completed"
        )
    
    @patch('structlog.get_logger')
    def test_log_error(self, mock_get_logger):
        """Test error logging helper."""
        mock_logger = mock_get_logger.return_value
        
        context = {"bucket": "test-bucket", "key": "test-key.mp3"}
        log_error(mock_logger, "S3AccessError", "Access denied", context)
        
        mock_logger.error.assert_called_once_with(
            "Error occurred",
            error_type="S3AccessError",
            error_message="Access denied",
            event_type="error",
            bucket="test-bucket",
            key="test-key.mp3"
        )
    
    @patch('structlog.get_logger')
    def test_log_error_without_context(self, mock_get_logger):
        """Test error logging helper without context."""
        mock_logger = mock_get_logger.return_value
        
        log_error(mock_logger, "GeneralError", "Something went wrong")
        
        mock_logger.error.assert_called_once_with(
            "Error occurred",
            error_type="GeneralError",
            error_message="Something went wrong",
            event_type="error"
        )