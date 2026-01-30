"""
Amazon Transcribe Operations Module

This module handles the actual operations with Amazon Transcribe service,
including starting transcription jobs, checking job status, and retrieving results.
All operations use boto3 with IAM role authentication.
"""

import boto3
import json
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
from .config import Config
from .logging_config import get_logger

logger = get_logger(__name__)


class TranscribeClient:
    """
    Amazon Transcribe client wrapper with error handling and logging.
    
    Provides a high-level interface for Transcribe operations with
    proper error handling and structured logging.
    """
    
    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize Transcribe client.
        
        Args:
            region_name: AWS region name (defaults to config value)
        """
        self.region_name = region_name or Config.get_aws_region()
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of boto3 Transcribe client."""
        if self._client is None:
            try:
                self._client = boto3.client('transcribe', region_name=self.region_name)
                logger.info(f"Initialized Transcribe client for region: {self.region_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Transcribe client: {str(e)}")
                raise
        return self._client


def start_transcription_job(job_parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start an Amazon Transcribe job.
    
    Creates and starts a new transcription job using the provided parameters.
    Uses IAM role authentication through boto3.
    
    Args:
        job_parameters: Complete job parameters dictionary
        
    Returns:
        Dict containing job information from Transcribe response
        
    Raises:
        ClientError: If Transcribe service returns an error
        BotoCoreError: If there's a connection or configuration error
        
    Requirements: 2.1, 2.2, 5.4, 5.5
    """
    transcribe_client = TranscribeClient()
    
    try:
        logger.info(f"Starting transcription job: {job_parameters['TranscriptionJobName']}")
        logger.debug(f"Job parameters: {json.dumps(job_parameters, indent=2)}")
        
        response = transcribe_client.client.start_transcription_job(**job_parameters)
        
        job_info = response['TranscriptionJob']
        logger.info(f"Successfully started job {job_info['TranscriptionJobName']} "
                   f"with status: {job_info['TranscriptionJobStatus']}")
        
        return job_info
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        logger.error(f"Transcribe service error [{error_code}]: {error_message}")
        logger.error(f"Failed job parameters: {job_parameters['TranscriptionJobName']}")
        
        # Re-raise with context
        raise ClientError(
            error_response={
                'Error': {
                    'Code': error_code,
                    'Message': f"Failed to start transcription job: {error_message}"
                }
            },
            operation_name='StartTranscriptionJob'
        )
    
    except BotoCoreError as e:
        logger.error(f"AWS connection error: {str(e)}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error starting transcription job: {str(e)}")
        raise


def get_transcription_job_status(job_name: str) -> Dict[str, Any]:
    """
    Get the status and details of a transcription job.
    
    Retrieves current job information including status, progress,
    and results location if completed.
    
    Args:
        job_name: The transcription job name
        
    Returns:
        Dict containing job status and details
        
    Raises:
        ClientError: If job not found or service error
        BotoCoreError: If there's a connection error
        
    Requirements: 3.1, 5.4, 5.5
    """
    transcribe_client = TranscribeClient()
    
    try:
        logger.debug(f"Checking status for job: {job_name}")
        
        response = transcribe_client.client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        
        job_info = response['TranscriptionJob']
        status = job_info['TranscriptionJobStatus']
        
        logger.info(f"Job {job_name} status: {status}")
        
        # Log additional details based on status
        if status == 'COMPLETED':
            transcript_uri = job_info.get('Transcript', {}).get('TranscriptFileUri')
            logger.info(f"Job completed. Transcript available at: {transcript_uri}")
        elif status == 'FAILED':
            failure_reason = job_info.get('FailureReason', 'Unknown')
            logger.error(f"Job failed. Reason: {failure_reason}")
        
        return job_info
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'BadRequestException':
            logger.error(f"Job not found: {job_name}")
        else:
            logger.error(f"Error checking job status [{error_code}]: {error_message}")
        
        raise
    
    except BotoCoreError as e:
        logger.error(f"AWS connection error while checking job status: {str(e)}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error checking job status: {str(e)}")
        raise


def get_transcription_result(job_name: str) -> Optional[str]:
    """
    Get the transcript file URI for a completed job.
    
    Retrieves the S3 URI where the transcription results are stored.
    Only works for jobs in COMPLETED status.
    
    Args:
        job_name: The transcription job name
        
    Returns:
        S3 URI of the transcript file, or None if job not completed
        
    Raises:
        ClientError: If job not found or service error
        ValueError: If job is not in completed status
        
    Requirements: 3.1
    """
    try:
        job_info = get_transcription_job_status(job_name)
        
        status = job_info['TranscriptionJobStatus']
        
        if status != 'COMPLETED':
            logger.warning(f"Job {job_name} is not completed (status: {status})")
            return None
        
        transcript_uri = job_info.get('Transcript', {}).get('TranscriptFileUri')
        
        if not transcript_uri:
            logger.error(f"No transcript URI found for completed job: {job_name}")
            raise ValueError(f"Completed job {job_name} has no transcript URI")
        
        logger.info(f"Retrieved transcript URI for job {job_name}: {transcript_uri}")
        return transcript_uri
        
    except Exception as e:
        logger.error(f"Error retrieving transcription result: {str(e)}")
        raise


def wait_for_job_completion(job_name: str, max_wait_seconds: int = 3600) -> Dict[str, Any]:
    """
    Wait for a transcription job to complete.
    
    Polls the job status until completion or timeout.
    This is primarily for testing and synchronous workflows.
    
    Args:
        job_name: The transcription job name
        max_wait_seconds: Maximum time to wait in seconds (default: 1 hour)
        
    Returns:
        Final job information dictionary
        
    Raises:
        TimeoutError: If job doesn't complete within max_wait_seconds
        ValueError: If job fails
        
    Note: In production Lambda, this should not be used due to execution time limits.
    """
    import time
    
    start_time = time.time()
    poll_interval = 30  # Poll every 30 seconds
    
    logger.info(f"Waiting for job completion: {job_name} (max {max_wait_seconds}s)")
    
    while time.time() - start_time < max_wait_seconds:
        try:
            job_info = get_transcription_job_status(job_name)
            status = job_info['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                logger.info(f"Job {job_name} completed successfully")
                return job_info
            elif status == 'FAILED':
                failure_reason = job_info.get('FailureReason', 'Unknown')
                logger.error(f"Job {job_name} failed: {failure_reason}")
                raise ValueError(f"Transcription job failed: {failure_reason}")
            elif status in ['IN_PROGRESS', 'QUEUED']:
                logger.debug(f"Job {job_name} still in progress, waiting...")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown job status: {status}")
                time.sleep(poll_interval)
                
        except ClientError as e:
            logger.error(f"Error while waiting for job: {str(e)}")
            raise
    
    # Timeout reached
    elapsed = time.time() - start_time
    logger.error(f"Job {job_name} did not complete within {max_wait_seconds}s (elapsed: {elapsed:.1f}s)")
    raise TimeoutError(f"Job {job_name} did not complete within {max_wait_seconds} seconds")


def list_transcription_jobs(status_filter: Optional[str] = None, max_results: int = 50) -> Dict[str, Any]:
    """
    List transcription jobs with optional status filtering.
    
    Retrieves a list of transcription jobs, optionally filtered by status.
    Useful for monitoring and debugging.
    
    Args:
        status_filter: Optional status to filter by ('QUEUED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing job summaries and pagination info
        
    Requirements: 5.4, 5.5
    """
    transcribe_client = TranscribeClient()
    
    try:
        params = {'MaxResults': max_results}
        if status_filter:
            params['Status'] = status_filter
        
        logger.debug(f"Listing transcription jobs with params: {params}")
        
        response = transcribe_client.client.list_transcription_jobs(**params)
        
        job_count = len(response.get('TranscriptionJobSummaries', []))
        logger.info(f"Retrieved {job_count} transcription jobs")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Error listing transcription jobs [{error_code}]: {error_message}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error listing transcription jobs: {str(e)}")
        raise