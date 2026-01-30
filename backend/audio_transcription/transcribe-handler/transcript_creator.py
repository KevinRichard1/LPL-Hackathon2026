"""
Transcript Creator module for saving clean text to S3.

This module handles uploading transcript text files to S3 with proper
encoding and content type settings.
"""

import boto3
from typing import Optional
from botocore.exceptions import ClientError, BotoCoreError

from .logging_config import get_logger

logger = get_logger(__name__)


class TranscriptCreator:
    """Creator for saving transcript text files to S3."""
    
    def __init__(self, s3_client=None):
        """
        Initialize the transcript creator.
        
        Args:
            s3_client: Optional boto3 S3 client. If None, creates a new client.
        """
        self.s3_client = s3_client or boto3.client('s3')
    
    def save_transcript_to_s3(
        self, 
        transcript_text: str, 
        bucket_name: str, 
        object_key: str,
        content_type: str = "text/plain"
    ) -> bool:
        """
        Save clean transcript text to S3 as a .txt file.
        
        Args:
            transcript_text: Clean transcript text to save
            bucket_name: S3 bucket name for transcript storage
            object_key: S3 object key for the transcript file
            content_type: MIME content type for the file (default: text/plain)
            
        Returns:
            True if upload successful, False otherwise
            
        Raises:
            ClientError: If S3 upload fails
            ValueError: If input parameters are invalid
        """
        try:
            # Validate input parameters
            if not transcript_text and transcript_text != "":
                raise ValueError("Transcript text cannot be None")
            
            if not bucket_name or not bucket_name.strip():
                raise ValueError("Bucket name cannot be empty")
            
            if not object_key or not object_key.strip():
                raise ValueError("Object key cannot be empty")
            
            # Ensure object key ends with .txt extension
            if not object_key.lower().endswith('.txt'):
                logger.warning(f"Object key '{object_key}' does not end with .txt extension")
            
            logger.info(f"Saving transcript to s3://{bucket_name}/{object_key}")
            
            # Encode text as UTF-8 bytes
            transcript_bytes = transcript_text.encode('utf-8')
            
            # Upload to S3 with proper content type and encoding
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=transcript_bytes,
                ContentType=content_type,
                ContentEncoding='utf-8',
                Metadata={
                    'source': 'audio-transcription-pipeline',
                    'encoding': 'utf-8',
                    'content-length': str(len(transcript_bytes))
                }
            )
            
            logger.info(f"Successfully saved transcript ({len(transcript_text)} characters) to s3://{bucket_name}/{object_key}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 upload error for {object_key}: {error_code} - {str(e)}")
            raise
        except UnicodeEncodeError as e:
            logger.error(f"UTF-8 encoding error for transcript text: {str(e)}")
            raise ValueError(f"Failed to encode transcript text as UTF-8: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving transcript: {str(e)}")
            raise
    
    def create_transcript_file(
        self, 
        transcript_text: str, 
        bucket_name: str, 
        filename: str
    ) -> bool:
        """
        Create a transcript file with automatic .txt extension handling.
        
        Args:
            transcript_text: Clean transcript text to save
            bucket_name: S3 bucket name for transcript storage
            filename: Base filename (will ensure .txt extension)
            
        Returns:
            True if upload successful, False otherwise
            
        Raises:
            ClientError: If S3 upload fails
            ValueError: If input parameters are invalid
        """
        try:
            # Ensure filename has .txt extension
            if not filename.lower().endswith('.txt'):
                if '.' in filename:
                    # Replace existing extension with .txt
                    base_name = filename.rsplit('.', 1)[0]
                    filename = f"{base_name}.txt"
                else:
                    # Add .txt extension
                    filename = f"{filename}.txt"
            
            return self.save_transcript_to_s3(
                transcript_text=transcript_text,
                bucket_name=bucket_name,
                object_key=filename,
                content_type="text/plain; charset=utf-8"
            )
            
        except Exception as e:
            logger.error(f"Error creating transcript file '{filename}': {str(e)}")
            raise
    
    def upload_transcript_with_metadata(
        self, 
        transcript_text: str, 
        bucket_name: str, 
        object_key: str,
        source_audio_key: Optional[str] = None,
        transcription_job_name: Optional[str] = None
    ) -> bool:
        """
        Upload transcript with additional metadata about the source.
        
        Args:
            transcript_text: Clean transcript text to save
            bucket_name: S3 bucket name for transcript storage
            object_key: S3 object key for the transcript file
            source_audio_key: Optional S3 key of the source audio file
            transcription_job_name: Optional Transcribe job name
            
        Returns:
            True if upload successful, False otherwise
            
        Raises:
            ClientError: If S3 upload fails
            ValueError: If input parameters are invalid
        """
        try:
            # Validate input parameters
            if not transcript_text and transcript_text != "":
                raise ValueError("Transcript text cannot be None")
            
            if not bucket_name or not bucket_name.strip():
                raise ValueError("Bucket name cannot be empty")
            
            if not object_key or not object_key.strip():
                raise ValueError("Object key cannot be empty")
            
            logger.info(f"Saving transcript with metadata to s3://{bucket_name}/{object_key}")
            
            # Encode text as UTF-8 bytes
            transcript_bytes = transcript_text.encode('utf-8')
            
            # Build metadata
            metadata = {
                'source': 'audio-transcription-pipeline',
                'encoding': 'utf-8',
                'content-length': str(len(transcript_bytes)),
                'character-count': str(len(transcript_text))
            }
            
            if source_audio_key:
                metadata['source-audio-key'] = source_audio_key
            
            if transcription_job_name:
                metadata['transcription-job-name'] = transcription_job_name
            
            # Upload to S3 with metadata
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=transcript_bytes,
                ContentType="text/plain; charset=utf-8",
                ContentEncoding='utf-8',
                Metadata=metadata
            )
            
            logger.info(f"Successfully saved transcript with metadata to s3://{bucket_name}/{object_key}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 upload error for {object_key}: {error_code} - {str(e)}")
            raise
        except UnicodeEncodeError as e:
            logger.error(f"UTF-8 encoding error for transcript text: {str(e)}")
            raise ValueError(f"Failed to encode transcript text as UTF-8: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving transcript with metadata: {str(e)}")
            raise


def create_transcript_creator(s3_client=None) -> TranscriptCreator:
    """
    Factory function to create a TranscriptCreator instance.
    
    Args:
        s3_client: Optional boto3 S3 client
        
    Returns:
        TranscriptCreator instance
    """
    return TranscriptCreator(s3_client=s3_client)