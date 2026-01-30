"""
Unit tests for Transcribe Operations module.

Tests the Amazon Transcribe service operations including job management,
status checking, and result retrieval with proper mocking of AWS services.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError
from audio_transcription.transcribe_operations import (
    TranscribeClient,
    start_transcription_job,
    get_transcription_job_status,
    get_transcription_result,
    wait_for_job_completion,
    list_transcription_jobs
)


class TestTranscribeClient:
    """Test TranscribeClient wrapper class."""
    
    def test_client_initialization(self):
        """Test client initialization with default region."""
        with patch('boto3.client') as mock_boto_client:
            client = TranscribeClient()
            # Access client property to trigger initialization
            _ = client.client
            
            mock_boto_client.assert_called_once_with('transcribe', region_name='us-east-1')
    
    def test_client_initialization_custom_region(self):
        """Test client initialization with custom region."""
        with patch('boto3.client') as mock_boto_client:
            client = TranscribeClient(region_name='eu-west-1')
            _ = client.client
            
            mock_boto_client.assert_called_once_with('transcribe', region_name='eu-west-1')
    
    def test_client_lazy_initialization(self):
        """Test that client is only initialized when accessed."""
        with patch('boto3.client') as mock_boto_client:
            client = TranscribeClient()
            # Client should not be initialized yet
            mock_boto_client.assert_not_called()
            
            # Access client property
            _ = client.client
            mock_boto_client.assert_called_once()
    
    def test_client_initialization_error(self):
        """Test error handling during client initialization."""
        with patch('boto3.client', side_effect=Exception("AWS credentials not found")):
            client = TranscribeClient()
            
            with pytest.raises(Exception, match="AWS credentials not found"):
                _ = client.client


class TestStartTranscriptionJob:
    """Test transcription job starting functionality."""
    
    def test_successful_job_start(self):
        """Test successful transcription job creation."""
        mock_response = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'test-job-123',
                'TranscriptionJobStatus': 'IN_PROGRESS',
                'MediaFormat': 'mp3',
                'LanguageCode': 'en-US'
            }
        }
        
        job_parameters = {
            'TranscriptionJobName': 'test-job-123',
            'Media': {'MediaFileUri': 's3://audio-uploads/test.mp3'},
            'MediaFormat': 'mp3',
            'LanguageCode': 'en-US',
            'OutputBucketName': 'transcripts-raw'
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.start_transcription_job.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = start_transcription_job(job_parameters)
            
            assert result == mock_response['TranscriptionJob']
            mock_client.client.start_transcription_job.assert_called_once_with(**job_parameters)
    
    def test_client_error_handling(self):
        """Test handling of Transcribe service errors."""
        error_response = {
            'Error': {
                'Code': 'BadRequestException',
                'Message': 'Invalid media format'
            }
        }
        
        job_parameters = {
            'TranscriptionJobName': 'test-job-123',
            'Media': {'MediaFileUri': 's3://audio-uploads/test.mp3'},
            'MediaFormat': 'invalid',
            'LanguageCode': 'en-US'
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.start_transcription_job.side_effect = ClientError(
                error_response, 'StartTranscriptionJob'
            )
            mock_client_class.return_value = mock_client
            
            with pytest.raises(ClientError) as exc_info:
                start_transcription_job(job_parameters)
            
            assert 'Failed to start transcription job' in str(exc_info.value)
    
    def test_botocore_error_handling(self):
        """Test handling of BotoCore connection errors."""
        job_parameters = {
            'TranscriptionJobName': 'test-job-123',
            'Media': {'MediaFileUri': 's3://audio-uploads/test.mp3'},
            'MediaFormat': 'mp3'
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.start_transcription_job.side_effect = BotoCoreError()
            mock_client_class.return_value = mock_client
            
            with pytest.raises(BotoCoreError):
                start_transcription_job(job_parameters)


class TestGetTranscriptionJobStatus:
    """Test job status checking functionality."""
    
    def test_get_completed_job_status(self):
        """Test getting status of completed job."""
        mock_response = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'test-job-123',
                'TranscriptionJobStatus': 'COMPLETED',
                'Transcript': {
                    'TranscriptFileUri': 's3://transcripts-raw/test-job-123.json'
                }
            }
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.get_transcription_job.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = get_transcription_job_status('test-job-123')
            
            assert result == mock_response['TranscriptionJob']
            assert result['TranscriptionJobStatus'] == 'COMPLETED'
    
    def test_get_failed_job_status(self):
        """Test getting status of failed job."""
        mock_response = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'test-job-123',
                'TranscriptionJobStatus': 'FAILED',
                'FailureReason': 'Audio file format not supported'
            }
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.get_transcription_job.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = get_transcription_job_status('test-job-123')
            
            assert result['TranscriptionJobStatus'] == 'FAILED'
            assert 'FailureReason' in result
    
    def test_job_not_found_error(self):
        """Test handling when job is not found."""
        error_response = {
            'Error': {
                'Code': 'BadRequestException',
                'Message': 'The requested job couldn\'t be found'
            }
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.get_transcription_job.side_effect = ClientError(
                error_response, 'GetTranscriptionJob'
            )
            mock_client_class.return_value = mock_client
            
            with pytest.raises(ClientError):
                get_transcription_job_status('nonexistent-job')


class TestGetTranscriptionResult:
    """Test transcription result retrieval."""
    
    def test_get_result_from_completed_job(self):
        """Test getting transcript URI from completed job."""
        mock_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'COMPLETED',
            'Transcript': {
                'TranscriptFileUri': 's3://transcripts-raw/test-job-123.json'
            }
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = mock_job_info
            
            result = get_transcription_result('test-job-123')
            
            assert result == 's3://transcripts-raw/test-job-123.json'
    
    def test_get_result_from_incomplete_job(self):
        """Test getting result from job that's not completed."""
        mock_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'IN_PROGRESS'
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = mock_job_info
            
            result = get_transcription_result('test-job-123')
            
            assert result is None
    
    def test_completed_job_without_transcript_uri(self):
        """Test error when completed job has no transcript URI."""
        mock_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'COMPLETED',
            'Transcript': {}  # Missing TranscriptFileUri
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = mock_job_info
            
            with pytest.raises(ValueError, match="has no transcript URI"):
                get_transcription_result('test-job-123')


class TestWaitForJobCompletion:
    """Test job completion waiting functionality."""
    
    def test_wait_for_successful_completion(self):
        """Test waiting for job that completes successfully."""
        completed_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'COMPLETED'
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = completed_job_info
            
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = wait_for_job_completion('test-job-123', max_wait_seconds=60)
                
                assert result == completed_job_info
    
    def test_wait_for_failed_job(self):
        """Test waiting for job that fails."""
        failed_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'FAILED',
            'FailureReason': 'Audio file corrupted'
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = failed_job_info
            
            with pytest.raises(ValueError, match="Transcription job failed"):
                wait_for_job_completion('test-job-123', max_wait_seconds=60)
    
    def test_wait_timeout(self):
        """Test timeout when job doesn't complete in time."""
        in_progress_job_info = {
            'TranscriptionJobName': 'test-job-123',
            'TranscriptionJobStatus': 'IN_PROGRESS'
        }
        
        with patch('audio_transcription.transcribe_operations.get_transcription_job_status') as mock_get_status:
            mock_get_status.return_value = in_progress_job_info
            
            with patch('time.sleep'):  # Mock sleep
                # Mock time.time to always return values that exceed timeout
                call_count = 0
                def mock_time():
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        return 0  # Start time
                    else:
                        return 61  # Always return time that exceeds timeout
                
                with patch('time.time', side_effect=mock_time):
                    with pytest.raises(TimeoutError, match="did not complete within"):
                        wait_for_job_completion('test-job-123', max_wait_seconds=60)


class TestListTranscriptionJobs:
    """Test transcription job listing functionality."""
    
    def test_list_all_jobs(self):
        """Test listing all transcription jobs."""
        mock_response = {
            'TranscriptionJobSummaries': [
                {
                    'TranscriptionJobName': 'job-1',
                    'TranscriptionJobStatus': 'COMPLETED'
                },
                {
                    'TranscriptionJobName': 'job-2',
                    'TranscriptionJobStatus': 'IN_PROGRESS'
                }
            ]
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.list_transcription_jobs.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = list_transcription_jobs()
            
            assert result == mock_response
            mock_client.client.list_transcription_jobs.assert_called_once_with(MaxResults=50)
    
    def test_list_jobs_with_status_filter(self):
        """Test listing jobs with status filter."""
        mock_response = {
            'TranscriptionJobSummaries': [
                {
                    'TranscriptionJobName': 'completed-job',
                    'TranscriptionJobStatus': 'COMPLETED'
                }
            ]
        }
        
        with patch('audio_transcription.transcribe_operations.TranscribeClient') as mock_client_class:
            mock_client = Mock()
            mock_client.client.list_transcription_jobs.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = list_transcription_jobs(status_filter='COMPLETED', max_results=10)
            
            assert result == mock_response
            mock_client.client.list_transcription_jobs.assert_called_once_with(
                MaxResults=10, Status='COMPLETED'
            )