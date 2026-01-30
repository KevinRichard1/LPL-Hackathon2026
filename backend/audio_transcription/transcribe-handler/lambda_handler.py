"""
AWS Lambda handler for the Audio Transcription Pipeline.

This module contains the main entry point for the Lambda function that processes
S3 events and orchestrates the audio transcription workflow.
"""

from typing import Any, Dict, List
import traceback

from .logging_config import setup_logging, get_logger
from .s3_event_parser import S3EventParser, S3EventRecord
from .file_format import should_process_file
from .transcribe_job_manager import create_transcription_job_config
from .transcribe_operations import start_transcription_job, get_transcription_job_status, get_transcription_result
from .json_parser import create_json_parser
from .transcript_creator import create_transcript_creator
from .filename_transformer import FilenameTransformer
from .config import Config


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function for processing S3 events.
    
    This function handles two types of events:
    1. S3 ObjectCreated events for audio files - starts transcription jobs
    2. S3 ObjectCreated events for Transcribe JSON results - processes completed transcriptions
    
    Args:
        event: AWS Lambda event containing S3 event notification
        context: AWS Lambda context object
        
    Returns:
        Dict containing status and processing results
        
    Requirements: All requirements
    """
    # Set up logging
    logger = setup_logging()
    
    request_id = context.aws_request_id if context else "local"
    
    try:
        logger.info(
            "Lambda function started",
            request_id=request_id,
            event_type="lambda_start",
            event_records_count=len(event.get("Records", []))
        )
        
        # Parse S3 event to extract file information
        try:
            s3_records = S3EventParser.parse_s3_event(event)
            logger.info(
                f"Parsed {len(s3_records)} S3 event records",
                request_id=request_id,
                event_type="s3_event_parsed"
            )
        except (ValueError, KeyError) as e:
            logger.error(
                f"Failed to parse S3 event: {str(e)}",
                request_id=request_id,
                event_type="s3_event_parse_error"
            )
            return {
                "statusCode": 400,
                "body": f"Invalid S3 event format: {str(e)}"
            }
        
        # Filter for object creation events only
        create_records = S3EventParser.filter_create_events(s3_records)
        logger.info(
            f"Found {len(create_records)} object creation events",
            request_id=request_id,
            event_type="create_events_filtered"
        )
        
        # Process each file independently
        processed_files = []
        skipped_files = []
        failed_files = []
        
        for record in create_records:
            try:
                # Determine if this is an audio file or transcription result
                if _is_transcription_result(record):
                    result = _process_transcription_result(record, request_id, logger)
                else:
                    result = _process_audio_file(record, request_id, logger)
                
                if result["processed"]:
                    processed_files.append(result)
                else:
                    skipped_files.append(result)
            except Exception as e:
                logger.error(
                    f"Failed to process file {record.object_key}: {str(e)}",
                    request_id=request_id,
                    event_type="file_processing_error",
                    object_key=record.object_key,
                    bucket_name=record.bucket_name,
                    error_details=str(e)
                )
                failed_files.append({
                    "object_key": record.object_key,
                    "bucket_name": record.bucket_name,
                    "error": str(e),
                    "processed": False
                })
        
        # Log final processing summary
        logger.info(
            "Lambda function completed",
            request_id=request_id,
            event_type="lambda_success",
            processed_count=len(processed_files),
            skipped_count=len(skipped_files),
            failed_count=len(failed_files),
            total_records=len(create_records)
        )
        
        return {
            "statusCode": 200,
            "body": {
                "message": "Processing completed",
                "processed": len(processed_files),
                "skipped": len(skipped_files),
                "failed": len(failed_files),
                "total": len(create_records),
                "processed_files": [f["object_key"] for f in processed_files],
                "skipped_files": [f["object_key"] for f in skipped_files],
                "failed_files": [f["object_key"] for f in failed_files]
            }
        }
        
    except Exception as e:
        # Log full stack trace for unexpected errors
        error_trace = traceback.format_exc()
        logger.error(
            "Lambda function failed with unexpected error",
            error=str(e),
            request_id=request_id,
            event_type="lambda_error",
            stack_trace=error_trace
        )
        
        return {
            "statusCode": 500,
            "body": f"Processing failed: {str(e)}"
        }


def _is_transcription_result(record: S3EventRecord) -> bool:
    """
    Determine if the S3 event is for a transcription result JSON file.
    
    Args:
        record: S3EventRecord to check
        
    Returns:
        True if this is a transcription result, False if it's an audio file
    """
    # Transcription results are JSON files in the transcript storage bucket
    transcript_bucket = Config.get_transcript_storage_bucket()
    return (record.bucket_name == transcript_bucket and 
            record.object_key.lower().endswith('.json'))


def _process_audio_file(record: S3EventRecord, request_id: str, logger) -> Dict[str, Any]:
    """
    Process a single audio file from S3 event by starting a transcription job.
    
    Args:
        record: S3EventRecord containing file information
        request_id: Lambda request ID for logging correlation
        logger: Logger instance
        
    Returns:
        Dict containing processing results
        
    Raises:
        Exception: If processing fails
    """
    object_key = record.object_key
    bucket_name = record.bucket_name
    
    logger.info(
        f"Processing audio file: {object_key}",
        request_id=request_id,
        event_type="audio_file_processing_start",
        object_key=object_key,
        bucket_name=bucket_name,
        object_size=record.object_size
    )
    
    # Check if file should be processed (supported audio format)
    if not should_process_file(object_key):
        logger.info(
            f"Skipping unsupported file format: {object_key}",
            request_id=request_id,
            event_type="file_skipped_format",
            object_key=object_key
        )
        return {
            "object_key": object_key,
            "bucket_name": bucket_name,
            "processed": False,
            "reason": "unsupported_format",
            "file_type": "audio"
        }
    
    # Validate bucket name matches expected audio upload bucket
    expected_bucket = Config.get_audio_upload_bucket()
    if bucket_name != expected_bucket:
        logger.warning(
            f"File from unexpected bucket: {bucket_name} (expected: {expected_bucket})",
            request_id=request_id,
            event_type="unexpected_bucket",
            object_key=object_key,
            actual_bucket=bucket_name,
            expected_bucket=expected_bucket
        )
        # Continue processing anyway, but log the warning
    
    # Create transcription job configuration
    try:
        job_config = create_transcription_job_config(object_key)
        job_name = job_config["job_name"]
        job_parameters = job_config["parameters"]
        
        logger.info(
            f"Created transcription job config: {job_name}",
            request_id=request_id,
            event_type="job_config_created",
            job_name=job_name,
            object_key=object_key,
            media_format=job_parameters["MediaFormat"]
        )
    except Exception as e:
        logger.error(
            f"Failed to create job config for {object_key}: {str(e)}",
            request_id=request_id,
            event_type="job_config_error",
            object_key=object_key
        )
        raise
    
    # Start transcription job
    try:
        job_info = start_transcription_job(job_parameters)
        
        logger.info(
            f"Started transcription job: {job_name}",
            request_id=request_id,
            event_type="transcription_job_started",
            job_name=job_name,
            object_key=object_key,
            job_status=job_info.get("TranscriptionJobStatus"),
            input_uri=job_parameters["Media"]["MediaFileUri"]
        )
        
        return {
            "object_key": object_key,
            "bucket_name": bucket_name,
            "job_name": job_name,
            "job_status": job_info.get("TranscriptionJobStatus"),
            "processed": True,
            "reason": "transcription_job_started",
            "file_type": "audio"
        }
        
    except Exception as e:
        logger.error(
            f"Failed to start transcription job for {object_key}: {str(e)}",
            request_id=request_id,
            event_type="transcription_job_error",
            job_name=job_name,
            object_key=object_key
        )
        raise


def _process_transcription_result(record: S3EventRecord, request_id: str, logger) -> Dict[str, Any]:
    """
    Process a transcription result JSON file by extracting text and creating transcript.
    
    Args:
        record: S3EventRecord containing JSON file information
        request_id: Lambda request ID for logging correlation
        logger: Logger instance
        
    Returns:
        Dict containing processing results
        
    Raises:
        Exception: If processing fails
    """
    object_key = record.object_key
    bucket_name = record.bucket_name
    
    logger.info(
        f"Processing transcription result: {object_key}",
        request_id=request_id,
        event_type="transcription_result_processing_start",
        object_key=object_key,
        bucket_name=bucket_name
    )
    
    # Extract job name from JSON filename (Transcribe uses job name as filename)
    json_filename = FilenameTransformer.extract_base_filename(object_key)
    job_name = json_filename.replace('.json', '') if json_filename.endswith('.json') else json_filename
    
    try:
        # Parse JSON and extract transcript text
        json_parser = create_json_parser()
        transcript_text = json_parser.parse_transcribe_result(bucket_name, object_key)
        
        logger.info(
            f"Extracted transcript text ({len(transcript_text)} characters)",
            request_id=request_id,
            event_type="transcript_text_extracted",
            job_name=job_name,
            text_length=len(transcript_text)
        )
        
        # Determine original audio filename from job name
        # Job names follow pattern: transcribe-{base_name}-{timestamp}-{uuid}
        original_audio_filename = _extract_original_filename_from_job_name(job_name)
        
        # Transform to transcript filename
        transcript_filename = FilenameTransformer.audio_to_transcript_filename(original_audio_filename)
        
        logger.info(
            f"Generated transcript filename: {transcript_filename}",
            request_id=request_id,
            event_type="transcript_filename_generated",
            original_filename=original_audio_filename,
            transcript_filename=transcript_filename
        )
        
        # Save transcript to S3
        transcript_creator = create_transcript_creator()
        transcript_bucket = Config.get_transcript_storage_bucket()
        
        success = transcript_creator.upload_transcript_with_metadata(
            transcript_text=transcript_text,
            bucket_name=transcript_bucket,
            object_key=transcript_filename,
            source_audio_key=original_audio_filename,
            transcription_job_name=job_name
        )
        
        if success:
            logger.info(
                f"Successfully created transcript file: {transcript_filename}",
                request_id=request_id,
                event_type="transcript_file_created",
                transcript_filename=transcript_filename,
                job_name=job_name,
                transcript_bucket=transcript_bucket
            )
            
            return {
                "object_key": object_key,
                "bucket_name": bucket_name,
                "job_name": job_name,
                "transcript_filename": transcript_filename,
                "transcript_length": len(transcript_text),
                "processed": True,
                "reason": "transcript_created",
                "file_type": "transcription_result"
            }
        else:
            raise Exception("Failed to upload transcript to S3")
            
    except Exception as e:
        logger.error(
            f"Failed to process transcription result {object_key}: {str(e)}",
            request_id=request_id,
            event_type="transcription_result_error",
            job_name=job_name,
            object_key=object_key
        )
        raise


def _extract_original_filename_from_job_name(job_name: str) -> str:
    """
    Extract original audio filename from transcription job name.
    
    Job names follow pattern: transcribe-{base_name}-{timestamp}-{uuid}
    This function extracts the base_name part and adds a default extension.
    
    Args:
        job_name: Transcription job name
        
    Returns:
        Original audio filename with extension
    """
    # Split job name and extract base name
    parts = job_name.split('-')
    
    if len(parts) >= 2 and parts[0] == 'transcribe':
        # Extract base name (everything between 'transcribe-' and the timestamp)
        # Find the timestamp part (format: YYYYMMDD)
        base_parts = []
        for i, part in enumerate(parts[1:], 1):
            # Check if this looks like a timestamp (8 digits)
            if len(part) == 8 and part.isdigit():
                break
            base_parts.append(part)
        
        if base_parts:
            base_name = '-'.join(base_parts)
            # Add default extension (we'll assume mp3 since we can't determine from job name)
            return f"{base_name}.mp3"
    
    # Fallback: use job name as base
    return f"{job_name}.mp3"


# Additional utility functions for complete workflow integration

def process_completed_transcription_job(job_name: str, request_id: str = "manual") -> Dict[str, Any]:
    """
    Process a completed transcription job by retrieving results and creating transcript.
    
    This function can be called directly for manual processing or testing.
    
    Args:
        job_name: Name of the completed transcription job
        request_id: Request ID for logging correlation
        
    Returns:
        Dict containing processing results
        
    Raises:
        Exception: If processing fails
    """
    logger = get_logger(__name__)
    
    try:
        logger.info(
            f"Processing completed job: {job_name}",
            request_id=request_id,
            event_type="manual_job_processing_start",
            job_name=job_name
        )
        
        # Get job status and result URI
        job_info = get_transcription_job_status(job_name)
        
        if job_info["TranscriptionJobStatus"] != "COMPLETED":
            raise ValueError(f"Job {job_name} is not completed (status: {job_info['TranscriptionJobStatus']})")
        
        # Get transcript URI
        transcript_uri = get_transcription_result(job_name)
        if not transcript_uri:
            raise ValueError(f"No transcript URI found for job {job_name}")
        
        # Parse S3 URI to get bucket and key
        # URI format: s3://bucket-name/path/to/file.json
        if not transcript_uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI format: {transcript_uri}")
        
        uri_parts = transcript_uri[5:].split('/', 1)  # Remove 's3://' and split
        if len(uri_parts) != 2:
            raise ValueError(f"Invalid S3 URI format: {transcript_uri}")
        
        result_bucket, result_key = uri_parts
        
        # Create a mock S3EventRecord for processing
        from datetime import datetime, timezone
        mock_record = S3EventRecord(
            bucket_name=result_bucket,
            object_key=result_key,
            event_name="ObjectCreated:Put",
            event_time=datetime.now(timezone.utc)
        )
        
        # Process the transcription result
        result = _process_transcription_result(mock_record, request_id, logger)
        
        logger.info(
            f"Successfully processed completed job: {job_name}",
            request_id=request_id,
            event_type="manual_job_processing_success",
            job_name=job_name
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Failed to process completed job {job_name}: {str(e)}",
            request_id=request_id,
            event_type="manual_job_processing_error",
            job_name=job_name
        )
        raise