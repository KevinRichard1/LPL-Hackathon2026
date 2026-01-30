"""
JSON Parser module for Amazon Transcribe results.

This module handles downloading Transcribe JSON results from S3,
parsing the nested JSON structure, and extracting clean transcript text.
"""

import json
import re
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError

from .logging_config import get_logger

logger = get_logger(__name__)


class TranscribeJSONParser:
    """Parser for Amazon Transcribe JSON output files."""
    
    def __init__(self, s3_client=None):
        """
        Initialize the JSON parser.
        
        Args:
            s3_client: Optional boto3 S3 client. If None, creates a new client.
        """
        self.s3_client = s3_client or boto3.client('s3')
    
    def download_transcribe_json(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """
        Download and parse Transcribe JSON results from S3.
        
        Args:
            bucket_name: S3 bucket containing the JSON file
            object_key: S3 object key for the JSON file
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            ClientError: If S3 access fails
            json.JSONDecodeError: If JSON parsing fails
            ValueError: If the downloaded content is invalid
        """
        try:
            logger.info(f"Downloading Transcribe JSON from s3://{bucket_name}/{object_key}")
            
            # Download the JSON file from S3
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            json_content = response['Body'].read().decode('utf-8')
            
            if not json_content.strip():
                raise ValueError(f"Empty JSON content downloaded from s3://{bucket_name}/{object_key}")
            
            # Parse the JSON content
            transcribe_data = json.loads(json_content)
            
            logger.info(f"Successfully parsed Transcribe JSON with job name: {transcribe_data.get('jobName', 'unknown')}")
            return transcribe_data
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 access error downloading {object_key}: {error_code} - {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for {object_key}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading Transcribe JSON: {str(e)}")
            raise
    
    def extract_transcript_text(self, transcribe_data: Dict[str, Any]) -> str:
        """
        Extract clean transcript text from Transcribe JSON structure.
        
        Args:
            transcribe_data: Parsed Transcribe JSON data
            
        Returns:
            Clean transcript text
            
        Raises:
            KeyError: If required JSON structure is missing
            ValueError: If transcript data is invalid
        """
        try:
            # Navigate the nested JSON structure to find transcript text
            results = transcribe_data.get('results')
            if results is None:
                raise KeyError("Missing 'results' field in Transcribe JSON")
            
            transcripts = results.get('transcripts')
            if transcripts is None or not isinstance(transcripts, list):
                raise KeyError("Missing or invalid 'transcripts' field in results")
            
            if len(transcripts) == 0:
                logger.warning("Empty transcripts array in Transcribe JSON")
                return ""
            
            # Extract the main transcript text
            main_transcript = transcripts[0].get('transcript')
            if main_transcript is None:
                raise KeyError("Missing 'transcript' field in first transcript entry")
            
            if not isinstance(main_transcript, str):
                raise ValueError(f"Transcript text is not a string: {type(main_transcript)}")
            
            # Clean the transcript text
            cleaned_text = self._clean_transcript_text(main_transcript)
            
            logger.info(f"Extracted transcript text ({len(cleaned_text)} characters)")
            return cleaned_text
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error extracting transcript text: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting transcript text: {str(e)}")
            raise
    
    def _clean_transcript_text(self, raw_text: str) -> str:
        """
        Clean transcript text by removing formatting artifacts.
        
        Args:
            raw_text: Raw transcript text from Transcribe
            
        Returns:
            Cleaned transcript text
        """
        if not raw_text:
            return ""
        
        # Remove extra whitespace and normalize line endings
        cleaned = re.sub(r'\s+', ' ', raw_text.strip())
        
        # Remove common formatting artifacts that might appear in transcripts
        # Remove multiple consecutive periods (ellipsis artifacts)
        cleaned = re.sub(r'\.{3,}', '...', cleaned)
        
        # Remove excessive punctuation repetition
        cleaned = re.sub(r'([!?])\1{2,}', r'\1', cleaned)
        
        # Normalize quotation marks
        cleaned = re.sub(r'["""]', '"', cleaned)
        cleaned = re.sub(r"[''']", "'", cleaned)
        
        # Remove any remaining control characters except newlines and tabs
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        return cleaned.strip()
    
    def parse_transcribe_result(self, bucket_name: str, object_key: str) -> str:
        """
        Complete workflow: download JSON from S3 and extract clean text.
        
        Args:
            bucket_name: S3 bucket containing the JSON file
            object_key: S3 object key for the JSON file
            
        Returns:
            Clean transcript text
            
        Raises:
            ClientError: If S3 access fails
            json.JSONDecodeError: If JSON parsing fails
            KeyError: If required JSON structure is missing
            ValueError: If transcript data is invalid
        """
        transcribe_data = self.download_transcribe_json(bucket_name, object_key)
        return self.extract_transcript_text(transcribe_data)


def create_json_parser(s3_client=None) -> TranscribeJSONParser:
    """
    Factory function to create a TranscribeJSONParser instance.
    
    Args:
        s3_client: Optional boto3 S3 client
        
    Returns:
        TranscribeJSONParser instance
    """
    return TranscribeJSONParser(s3_client=s3_client)