"""
Tests for the Lambda handler module.
"""

import pytest
from unittest.mock import patch, Mock

from audio_transcription.lambda_handler import lambda_handler


class TestLambdaHandler:
    """Test cases for the Lambda handler function."""
    
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_success(self, mock_setup_logging, mock_lambda_context, sample_s3_event):
        """Test successful Lambda handler execution."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        result = lambda_handler(sample_s3_event, mock_lambda_context)
        
        assert result["statusCode"] == 200
        assert "Processing completed successfully" in result["body"]
        
        # Verify logging calls
        mock_logger.info.assert_any_call(
            "Lambda function started",
            request_id="test-request-id-123",
            event_type="lambda_start"
        )
        mock_logger.info.assert_any_call(
            "Lambda function completed successfully",
            request_id="test-request-id-123",
            event_type="lambda_success"
        )
    
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_with_exception(self, mock_setup_logging, mock_lambda_context, sample_s3_event):
        """Test Lambda handler with exception."""
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
        mock_logger.error.assert_called_once_with(
            "Lambda function failed",
            error="Test error",
            request_id="test-request-id-123",
            event_type="lambda_error"
        )
    
    @patch('audio_transcription.lambda_handler.setup_logging')
    def test_lambda_handler_without_context(self, mock_setup_logging, sample_s3_event):
        """Test Lambda handler without context (local testing)."""
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        result = lambda_handler(sample_s3_event, None)
        
        assert result["statusCode"] == 200
        
        # Verify logging with local request ID
        mock_logger.info.assert_any_call(
            "Lambda function started",
            request_id="local",
            event_type="lambda_start"
        )