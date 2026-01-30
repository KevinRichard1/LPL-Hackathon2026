"""
Unit tests for the JSON Parser module.
"""

import json
import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from audio_transcription.json_parser import TranscribeJSONParser, create_json_parser


class TestTranscribeJSONParser:
    """Test cases for TranscribeJSONParser class."""
    
    def test_init_with_default_client(self):
        """Test parser initialization with default S3 client."""
        with patch('audio_transcription.json_parser.boto3.client') as mock_boto3:
            mock_client = Mock()
            mock_boto3.return_value = mock_client
            
            parser = TranscribeJSONParser()
            
            assert parser.s3_client == mock_client
            mock_boto3.assert_called_once_with('s3')
    
    def test_init_with_custom_client(self):
        """Test parser initialization with custom S3 client."""
        mock_client = Mock()
        parser = TranscribeJSONParser(s3_client=mock_client)
        
        assert parser.s3_client == mock_client
    
    def test_download_transcribe_json_success(self, sample_transcribe_json_output):
        """Test successful JSON download and parsing."""
        mock_s3_client = Mock()
        mock_response = {
            'Body': Mock()
        }
        json_content = json.dumps(sample_transcribe_json_output)
        mock_response['Body'].read.return_value = json_content.encode('utf-8')
        mock_s3_client.get_object.return_value = mock_response
        
        parser = TranscribeJSONParser(s3_client=mock_s3_client)
        result = parser.download_transcribe_json("test-bucket", "test-key.json")
        
        assert result == sample_transcribe_json_output
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket", 
            Key="test-key.json"
        )
    
    def test_download_transcribe_json_s3_error(self):
        """Test S3 access error handling."""
        mock_s3_client = Mock()
        mock_s3_client.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey'}}, 
            'GetObject'
        )
        
        parser = TranscribeJSONParser(s3_client=mock_s3_client)
        
        with pytest.raises(ClientError):
            parser.download_transcribe_json("test-bucket", "nonexistent-key.json")
    
    def test_download_transcribe_json_empty_content(self):
        """Test handling of empty JSON content."""
        mock_s3_client = Mock()
        mock_response = {
            'Body': Mock()
        }
        mock_response['Body'].read.return_value = b''
        mock_s3_client.get_object.return_value = mock_response
        
        parser = TranscribeJSONParser(s3_client=mock_s3_client)
        
        with pytest.raises(ValueError, match="Empty JSON content"):
            parser.download_transcribe_json("test-bucket", "empty-file.json")
    
    def test_download_transcribe_json_invalid_json(self):
        """Test handling of invalid JSON content."""
        mock_s3_client = Mock()
        mock_response = {
            'Body': Mock()
        }
        mock_response['Body'].read.return_value = b'invalid json content'
        mock_s3_client.get_object.return_value = mock_response
        
        parser = TranscribeJSONParser(s3_client=mock_s3_client)
        
        with pytest.raises(json.JSONDecodeError):
            parser.download_transcribe_json("test-bucket", "invalid.json")
    
    def test_extract_transcript_text_success(self, sample_transcribe_json_output):
        """Test successful text extraction from valid JSON."""
        parser = TranscribeJSONParser()
        result = parser.extract_transcript_text(sample_transcribe_json_output)
        
        expected_text = "This is a sample transcript text for testing purposes."
        assert result == expected_text
    
    def test_extract_transcript_text_missing_results(self):
        """Test error handling when results field is missing."""
        parser = TranscribeJSONParser()
        invalid_data = {"jobName": "test-job"}
        
        with pytest.raises(KeyError, match="Missing 'results' field"):
            parser.extract_transcript_text(invalid_data)
    
    def test_extract_transcript_text_missing_transcripts(self):
        """Test error handling when transcripts field is missing."""
        parser = TranscribeJSONParser()
        invalid_data = {"results": {}}
        
        with pytest.raises(KeyError, match="Missing or invalid 'transcripts' field"):
            parser.extract_transcript_text(invalid_data)
    
    def test_extract_transcript_text_empty_transcripts(self):
        """Test handling of empty transcripts array."""
        parser = TranscribeJSONParser()
        data_with_empty_transcripts = {
            "results": {
                "transcripts": []
            }
        }
        
        result = parser.extract_transcript_text(data_with_empty_transcripts)
        assert result == ""
    
    def test_extract_transcript_text_missing_transcript_field(self):
        """Test error handling when transcript field is missing."""
        parser = TranscribeJSONParser()
        invalid_data = {
            "results": {
                "transcripts": [{}]
            }
        }
        
        with pytest.raises(KeyError, match="Missing 'transcript' field"):
            parser.extract_transcript_text(invalid_data)
    
    def test_extract_transcript_text_non_string_transcript(self):
        """Test error handling when transcript is not a string."""
        parser = TranscribeJSONParser()
        invalid_data = {
            "results": {
                "transcripts": [{"transcript": 123}]
            }
        }
        
        with pytest.raises(ValueError, match="Transcript text is not a string"):
            parser.extract_transcript_text(invalid_data)
    
    def test_clean_transcript_text_basic_cleaning(self):
        """Test basic text cleaning functionality."""
        parser = TranscribeJSONParser()
        
        # Test whitespace normalization
        raw_text = "  This   is    a   test.  "
        cleaned = parser._clean_transcript_text(raw_text)
        assert cleaned == "This is a test."
        
        # Test empty string
        assert parser._clean_transcript_text("") == ""
        assert parser._clean_transcript_text("   ") == ""
    
    def test_clean_transcript_text_formatting_artifacts(self):
        """Test removal of formatting artifacts."""
        parser = TranscribeJSONParser()
        
        # Test ellipsis normalization
        raw_text = "This is a test...... with ellipsis."
        cleaned = parser._clean_transcript_text(raw_text)
        assert cleaned == "This is a test... with ellipsis."
        
        # Test excessive punctuation
        raw_text = "Really!!! Are you sure???"
        cleaned = parser._clean_transcript_text(raw_text)
        assert cleaned == "Really! Are you sure?"
        
        # Test quotation mark normalization
        raw_text = """He said "hello" and 'goodbye'."""
        cleaned = parser._clean_transcript_text(raw_text)
        assert cleaned == """He said "hello" and 'goodbye'."""
    
    def test_parse_transcribe_result_success(self, sample_transcribe_json_output):
        """Test complete workflow from S3 download to text extraction."""
        mock_s3_client = Mock()
        mock_response = {
            'Body': Mock()
        }
        json_content = json.dumps(sample_transcribe_json_output)
        mock_response['Body'].read.return_value = json_content.encode('utf-8')
        mock_s3_client.get_object.return_value = mock_response
        
        parser = TranscribeJSONParser(s3_client=mock_s3_client)
        result = parser.parse_transcribe_result("test-bucket", "test-key.json")
        
        expected_text = "This is a sample transcript text for testing purposes."
        assert result == expected_text
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket", 
            Key="test-key.json"
        )


class TestCreateJSONParser:
    """Test cases for the factory function."""
    
    def test_create_json_parser_default(self):
        """Test factory function with default parameters."""
        with patch('audio_transcription.json_parser.boto3.client') as mock_boto3:
            mock_client = Mock()
            mock_boto3.return_value = mock_client
            
            parser = create_json_parser()
            
            assert isinstance(parser, TranscribeJSONParser)
            assert parser.s3_client == mock_client
    
    def test_create_json_parser_custom_client(self):
        """Test factory function with custom S3 client."""
        mock_client = Mock()
        parser = create_json_parser(s3_client=mock_client)
        
        assert isinstance(parser, TranscribeJSONParser)
        assert parser.s3_client == mock_client