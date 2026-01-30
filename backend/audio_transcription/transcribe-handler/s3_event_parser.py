"""
S3 Event Parser Module for Audio Transcription Pipeline.

This module provides functionality to parse S3 event notifications and extract
relevant information for processing audio files.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class S3EventRecord:
    """Represents a single S3 event record with extracted metadata."""
    
    bucket_name: str
    object_key: str
    event_name: str
    event_time: datetime
    object_size: Optional[int] = None
    event_version: Optional[str] = None
    aws_region: Optional[str] = None


class S3EventParser:
    """Parser for S3 event notifications."""
    
    @staticmethod
    def parse_s3_event(event: Dict[str, Any]) -> List[S3EventRecord]:
        """
        Parse S3 event JSON structure and extract relevant information.
        
        Args:
            event: The S3 event notification dictionary
            
        Returns:
            List of S3EventRecord objects containing extracted metadata
            
        Raises:
            ValueError: If the event structure is invalid or missing required fields
            KeyError: If required fields are missing from the event
        """
        if not isinstance(event, dict):
            raise ValueError("Event must be a dictionary")
        
        if "Records" not in event:
            raise ValueError("Event must contain 'Records' field")
        
        records = event["Records"]
        if not isinstance(records, list):
            raise ValueError("Records must be a list")
        
        parsed_records = []
        
        for record in records:
            try:
                parsed_record = S3EventParser._parse_single_record(record)
                parsed_records.append(parsed_record)
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid record structure: {e}")
        
        return parsed_records
    
    @staticmethod
    def _parse_single_record(record: Dict[str, Any]) -> S3EventRecord:
        """
        Parse a single S3 event record.
        
        Args:
            record: Single record from S3 event
            
        Returns:
            S3EventRecord object with extracted metadata
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid
        """
        # Extract required fields
        s3_data = record["s3"]
        bucket_data = s3_data["bucket"]
        object_data = s3_data["object"]
        
        bucket_name = bucket_data["name"]
        object_key = object_data["key"]
        event_name = record["eventName"]
        event_time_str = record["eventTime"]
        
        # Validate required fields
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        if not object_key:
            raise ValueError("Object key cannot be empty")
        if not event_name:
            raise ValueError("Event name cannot be empty")
        
        # Parse event time
        try:
            event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"Invalid event time format: {e}")
        
        # Extract optional fields
        object_size = object_data.get("size")
        event_version = record.get("eventVersion")
        aws_region = record.get("awsRegion")
        
        return S3EventRecord(
            bucket_name=bucket_name,
            object_key=object_key,
            event_name=event_name,
            event_time=event_time,
            object_size=object_size,
            event_version=event_version,
            aws_region=aws_region
        )
    
    @staticmethod
    def extract_bucket_name(event: Dict[str, Any]) -> str:
        """
        Extract bucket name from the first record in S3 event.
        
        Args:
            event: The S3 event notification dictionary
            
        Returns:
            Bucket name from the first record
            
        Raises:
            ValueError: If event is invalid or has no records
        """
        records = S3EventParser.parse_s3_event(event)
        if not records:
            raise ValueError("No records found in event")
        return records[0].bucket_name
    
    @staticmethod
    def extract_object_keys(event: Dict[str, Any]) -> List[str]:
        """
        Extract all object keys from S3 event records.
        
        Args:
            event: The S3 event notification dictionary
            
        Returns:
            List of object keys from all records
        """
        records = S3EventParser.parse_s3_event(event)
        return [record.object_key for record in records]
    
    @staticmethod
    def filter_create_events(records: List[S3EventRecord]) -> List[S3EventRecord]:
        """
        Filter records to include only object creation events.
        
        Args:
            records: List of S3EventRecord objects
            
        Returns:
            Filtered list containing only creation events
        """
        create_event_prefixes = ["ObjectCreated:", "s3:ObjectCreated:"]
        
        filtered_records = []
        for record in records:
            if any(record.event_name.startswith(prefix) for prefix in create_event_prefixes):
                filtered_records.append(record)
        
        return filtered_records