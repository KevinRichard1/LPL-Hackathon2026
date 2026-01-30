"""
Tests for the Lambda handler module.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock

from audio_transcription.lambda_handler import lambda_handler, _process_audio_file, _process_transcription_result, _is_transcription_result
from audio_transcription.s3_event_parser import S3EventRecord
from datetime import datetime, timezone


class TestLambdaHandler:
    """Test cases for the Lambda handler function."""
    
    @patch('audio_transcription.lambda_handler.S3EventParser')
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_success_audio_file(self, mock_setup_logging, mock_parser, mock_lambda_context, sample_s3_event):
        """Test successful Lambda handler execution with audio file."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # Mock S3 event parsing
        mock_record = S3EventRecord(
            bucket_name="audio-uploads",
            object_key="test.mp3",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        mock_parser.parse_s3_event.return_value = [mock_record]
        mock_parser.filter_create_events.return_value = [mock_record]
        
        # Mock the audio file processing
        with patch('audio_transcription.lambda_handler._process_audio_file') as mock_process_audio:
            with patch('audio_transcription.lambda_handler._is_transcription_result', return_value=False):
                mock_process_audio.return_value = {
                    "object_key": "test.mp3",
                    "bucket_name": "audio-uploads",
                    "processed": True,
                    "reason": "transcription_job_started",
                    "file_type": "audio"
                }
                
                result = lambda_handler(sample_s3_event, mock_lambda_context)
        
        assert result["statusCode"] == 200
        assert result["body"]["processed"] == 1
        assert result["body"]["skipped"] == 0
        assert result["body"]["failed"] == 0
        
        # Verify logging calls
        mock_logger.info.assert_any_call(
            "Lambda function started",
            request_id="test-request-id-123",
            event_type="lambda_start",
            event_records_count=1
        )
    
    @patch('audio_transcription.lambda_handler.S3EventParser')
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_invalid_s3_event(self, mock_setup_logging, mock_parser, mock_lambda_context):
        """Test Lambda handler with invalid S3 event."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # Mock S3 event parsing to raise ValueError
        mock_parser.parse_s3_event.side_effect = ValueError("Invalid event format")
        
        invalid_event = {"invalid": "event"}
        result = lambda_handler(invalid_event, mock_lambda_context)
        
        assert result["statusCode"] == 400
        assert "Invalid S3 event format" in result["body"]
        
        # Verify error logging
        mock_logger.error.assert_called_with(
            "Failed to parse S3 event: Invalid event format",
            request_id="test-request-id-123",
            event_type="s3_event_parse_error"
        )
    
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_with_exception(self, mock_setup_logging, mock_lambda_context, sample_s3_event):
        """Test Lambda handler with unexpected exception."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # Mock setup_logging to raise an exception after being called
        mock_setup_logging.side_effect = [mock_logger, Exception("Test error")]
        
        # Patch the logger.info method to raise an exception
        mock_logger.info.side_effect = Exception("Test error")
        
        result = lambda_handler(sample_s3_event, mock_lambda_context)
        
        assert result["statusCode"] == 500
        assert "Processing failed: Test error" in result["body"]
        
        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "Lambda function failed with unexpected error" in error_call[0][0]
    
    @patch('audio_transcription.lambda_handler.S3EventParser')
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_without_context(self, mock_setup_logging, mock_parser, sample_s3_event):
        """Test Lambda handler without context (local testing)."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # Mock empty records
        mock_parser.parse_s3_event.return_value = []
        mock_parser.filter_create_events.return_value = []
        
        result = lambda_handler(sample_s3_event, None)
        
        assert result["statusCode"] == 200
        
        # Verify logging with local request ID
        mock_logger.info.assert_any_call(
            "Lambda function started",
            request_id="local",
            event_type="lambda_start",
            event_records_count=1
        )


class TestProcessAudioFile:
    """Test cases for audio file processing."""
    
    @patch('audio_transcription.lambda_handler.start_transcription_job')
    @patch('audio_transcription.lambda_handler.create_transcription_job_config')
    @patch('audio_transcription.lambda_handler.should_process_file')
    def test_process_audio_file_success(self, mock_should_process, mock_create_config, mock_start_job):
        """Test successful audio file processing."""
        mock_logger = Mock()
        
        # Setup mocks
        mock_should_process.return_value = True
        mock_create_config.return_value = {
            "job_name": "test-job-123",
            "parameters": {
                "TranscriptionJobName": "test-job-123",
                "MediaFormat": "mp3",
                "Media": {"MediaFileUri": "s3://audio-uploads/test.mp3"}
            }
        }
        mock_start_job.return_value = {
            "TranscriptionJobStatus": "IN_PROGRESS"
        }
        
        record = S3EventRecord(
            bucket_name="audio-uploads",
            object_key="test.mp3",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc),
            object_size=1024
        )
        
        result = _process_audio_file(record, "test-request", mock_logger)
        
        assert result["processed"] is True
        assert result["object_key"] == "test.mp3"
        assert result["job_name"] == "test-job-123"
        assert result["file_type"] == "audio"
    
    @patch('audio_transcription.lambda_handler.should_process_file')
    def test_process_audio_file_unsupported_format(self, mock_should_process):
        """Test audio file processing with unsupported format."""
        mock_logger = Mock()
        mock_should_process.return_value = False
        
        record = S3EventRecord(
            bucket_name="audio-uploads",
            object_key="test.txt",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        result = _process_audio_file(record, "test-request", mock_logger)
        
        assert result["processed"] is False
        assert result["reason"] == "unsupported_format"
        assert result["file_type"] == "audio"


class TestProcessTranscriptionResult:
    """Test cases for transcription result processing."""
    
    @patch('audio_transcription.lambda_handler.create_transcript_creator')
    @patch('audio_transcription.lambda_handler.create_json_parser')
    @patch('audio_transcription.lambda_handler.FilenameTransformer')
    def test_process_transcription_result_success(self, mock_transformer, mock_json_parser, mock_creator):
        """Test successful transcription result processing."""
        mock_logger = Mock()
        
        # Setup mocks
        mock_parser_instance = Mock()
        mock_json_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_transcribe_result.return_value = "This is the transcript text."
        
        mock_transformer.extract_base_filename.return_value = "test-job-123.json"
        mock_transformer.audio_to_transcript_filename.return_value = "test.txt"
        
        mock_creator_instance = Mock()
        mock_creator.return_value = mock_creator_instance
        mock_creator_instance.upload_transcript_with_metadata.return_value = True
        
        record = S3EventRecord(
            bucket_name="transcripts-raw",
            object_key="test-job-123.json",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        result = _process_transcription_result(record, "test-request", mock_logger)
        
        assert result["processed"] is True
        assert result["transcript_filename"] == "test.txt"
        assert result["file_type"] == "transcription_result"


class TestIsTranscriptionResult:
    """Test cases for transcription result detection."""
    
    @patch('audio_transcription.lambda_handler.Config')
    def test_is_transcription_result_true(self, mock_config):
        """Test detection of transcription result file."""
        mock_config.get_transcript_storage_bucket.return_value = "transcripts-raw"
        
        record = S3EventRecord(
            bucket_name="transcripts-raw",
            object_key="test-job.json",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        result = _is_transcription_result(record)
        assert result is True
    
    @patch('audio_transcription.lambda_handler.Config')
    def test_is_transcription_result_false_wrong_bucket(self, mock_config):
        """Test detection with wrong bucket."""
        mock_config.get_transcript_storage_bucket.return_value = "transcripts-raw"
        
        record = S3EventRecord(
            bucket_name="audio-uploads",
            object_key="test.json",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        result = _is_transcription_result(record)
        assert result is False
    
    @patch('audio_transcription.lambda_handler.Config')
    def test_is_transcription_result_false_wrong_extension(self, mock_config):
        """Test detection with wrong file extension."""
        mock_config.get_transcript_storage_bucket.return_value = "transcripts-raw"
        
        record = S3EventRecord(
            bucket_name="transcripts-raw",
            object_key="test.mp3",
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        result = _is_transcription_result(record)
        assert result is False