"""
Unit tests for the Transcript Creator module.
"""

import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from audio_transcription.transcript_creator import TranscriptCreator, create_transcript_creator


class TestTranscriptCreator:
    """Test cases for TranscriptCreator class."""
    
    def test_init_with_default_client(self):
        """Test creator initialization with default S3 client."""
        with patch('audio_transcription.transcript_creator.boto3.client') as mock_boto3:
            mock_client = Mock()
            mock_boto3.return_value = mock_client
            
            creator = TranscriptCreator()
            
            assert creator.s3_client == mock_client
            mock_boto3.assert_called_once_with('s3')
    
    def test_init_with_custom_client(self):
        """Test creator initialization with custom S3 client."""
        mock_client = Mock()
        creator = TranscriptCreator(s3_client=mock_client)
        
        assert creator.s3_client == mock_client
    
    def test_save_transcript_to_s3_success(self):
        """Test successful transcript upload to S3."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        transcript_text = "This is a test transcript."
        bucket_name = "test-bucket"
        object_key = "test-transcript.txt"
        
        result = creator.save_transcript_to_s3(transcript_text, bucket_name, object_key)
        
        assert result is True
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=bucket_name,
            Key=object_key,
            Body=transcript_text.encode('utf-8'),
            ContentType="text/plain",
            ContentEncoding='utf-8',
            Metadata={
                'source': 'audio-transcription-pipeline',
                'encoding': 'utf-8',
                'content-length': str(len(transcript_text.encode('utf-8')))
            }
        )
    
    def test_save_transcript_to_s3_empty_text(self):
        """Test saving empty transcript text."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.save_transcript_to_s3("", "test-bucket", "empty.txt")
        
        assert result is True
        mock_s3_client.put_object.assert_called_once()
    
    def test_save_transcript_to_s3_none_text(self):
        """Test error handling with None transcript text."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        with pytest.raises(ValueError, match="Transcript text cannot be None"):
            creator.save_transcript_to_s3(None, "test-bucket", "test.txt")
    
    def test_save_transcript_to_s3_empty_bucket(self):
        """Test error handling with empty bucket name."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        with pytest.raises(ValueError, match="Bucket name cannot be empty"):
            creator.save_transcript_to_s3("test", "", "test.txt")
    
    def test_save_transcript_to_s3_empty_key(self):
        """Test error handling with empty object key."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        with pytest.raises(ValueError, match="Object key cannot be empty"):
            creator.save_transcript_to_s3("test", "bucket", "")
    
    def test_save_transcript_to_s3_non_txt_extension_warning(self):
        """Test warning when object key doesn't end with .txt."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        # This should work but log a warning
        result = creator.save_transcript_to_s3("test", "bucket", "file.json")
        
        assert result is True
        mock_s3_client.put_object.assert_called_once()
    
    def test_save_transcript_to_s3_s3_error(self):
        """Test S3 upload error handling."""
        mock_s3_client = Mock()
        mock_s3_client.put_object.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied'}}, 
            'PutObject'
        )
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        with pytest.raises(ClientError):
            creator.save_transcript_to_s3("test", "bucket", "test.txt")
    
    def test_save_transcript_to_s3_custom_content_type(self):
        """Test upload with custom content type."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.save_transcript_to_s3(
            "test", 
            "bucket", 
            "test.txt", 
            content_type="text/plain; charset=utf-8"
        )
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        assert call_args[1]['ContentType'] == "text/plain; charset=utf-8"
    
    def test_create_transcript_file_add_extension(self):
        """Test automatic .txt extension addition."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.create_transcript_file("test", "bucket", "filename")
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        assert call_args[1]['Key'] == "filename.txt"
        assert call_args[1]['ContentType'] == "text/plain; charset=utf-8"
    
    def test_create_transcript_file_replace_extension(self):
        """Test replacing existing extension with .txt."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.create_transcript_file("test", "bucket", "audio.mp3")
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        assert call_args[1]['Key'] == "audio.txt"
    
    def test_create_transcript_file_keep_txt_extension(self):
        """Test keeping existing .txt extension."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.create_transcript_file("test", "bucket", "transcript.txt")
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        assert call_args[1]['Key'] == "transcript.txt"
    
    def test_upload_transcript_with_metadata_basic(self):
        """Test upload with basic metadata."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.upload_transcript_with_metadata(
            "test transcript", 
            "bucket", 
            "test.txt"
        )
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        metadata = call_args[1]['Metadata']
        
        assert metadata['source'] == 'audio-transcription-pipeline'
        assert metadata['encoding'] == 'utf-8'
        assert metadata['character-count'] == '15'  # len("test transcript")
    
    def test_upload_transcript_with_metadata_full(self):
        """Test upload with full metadata."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        result = creator.upload_transcript_with_metadata(
            "test transcript", 
            "bucket", 
            "test.txt",
            source_audio_key="audio/test.mp3",
            transcription_job_name="job-123"
        )
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        metadata = call_args[1]['Metadata']
        
        assert metadata['source-audio-key'] == 'audio/test.mp3'
        assert metadata['transcription-job-name'] == 'job-123'
    
    def test_upload_transcript_with_metadata_validation_errors(self):
        """Test validation errors in metadata upload."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        # Test None text
        with pytest.raises(ValueError, match="Transcript text cannot be None"):
            creator.upload_transcript_with_metadata(None, "bucket", "test.txt")
        
        # Test empty bucket
        with pytest.raises(ValueError, match="Bucket name cannot be empty"):
            creator.upload_transcript_with_metadata("test", "", "test.txt")
        
        # Test empty key
        with pytest.raises(ValueError, match="Object key cannot be empty"):
            creator.upload_transcript_with_metadata("test", "bucket", "")
    
    def test_upload_transcript_with_metadata_s3_error(self):
        """Test S3 error handling in metadata upload."""
        mock_s3_client = Mock()
        mock_s3_client.put_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchBucket'}}, 
            'PutObject'
        )
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        with pytest.raises(ClientError):
            creator.upload_transcript_with_metadata("test", "bucket", "test.txt")
    
    def test_unicode_handling(self):
        """Test proper UTF-8 encoding of unicode characters."""
        mock_s3_client = Mock()
        creator = TranscriptCreator(s3_client=mock_s3_client)
        
        # Test with unicode characters
        unicode_text = "Hello 世界! Café résumé naïve"
        result = creator.save_transcript_to_s3(unicode_text, "bucket", "unicode.txt")
        
        assert result is True
        call_args = mock_s3_client.put_object.call_args
        uploaded_bytes = call_args[1]['Body']
        
        # Verify the bytes can be decoded back to the original text
        assert uploaded_bytes.decode('utf-8') == unicode_text


class TestCreateTranscriptCreator:
    """Test cases for the factory function."""
    
    def test_create_transcript_creator_default(self):
        """Test factory function with default parameters."""
        with patch('audio_transcription.transcript_creator.boto3.client') as mock_boto3:
            mock_client = Mock()
            mock_boto3.return_value = mock_client
            
            creator = create_transcript_creator()
            
            assert isinstance(creator, TranscriptCreator)
            assert creator.s3_client == mock_client
    
    def test_create_transcript_creator_custom_client(self):
        """Test factory function with custom S3 client."""
        mock_client = Mock()
        creator = create_transcript_creator(s3_client=mock_client)
        
        assert isinstance(creator, TranscriptCreator)
        assert creator.s3_client == mock_client