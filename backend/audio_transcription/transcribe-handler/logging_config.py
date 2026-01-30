"""
Logging configuration for Audio Transcription Pipeline.

This module provides structured JSON logging compatible with AWS CloudWatch
for monitoring and debugging purposes.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict

from .config import Config


class CloudWatchJSONFormatter(logging.Formatter):
    """Custom JSON formatter for CloudWatch compatibility."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for CloudWatch."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info"}:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def add_context_processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add contextual information to log entries."""
    event_dict["service"] = "audio-transcription-pipeline"
    event_dict["version"] = "1.0.0"
    return event_dict


def setup_logging() -> structlog.BoundLogger:
    """
    Set up structured logging for the Audio Transcription Pipeline.
    
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    )
    
    # Get root logger and set custom formatter
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setFormatter(CloudWatchJSONFormatter())
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            add_context_processor,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Optional logger name
        
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


def log_s3_event(logger: structlog.BoundLogger, bucket: str, key: str, event_name: str) -> None:
    """Log S3 event information."""
    logger.info(
        "S3 event received",
        bucket=bucket,
        object_key=key,
        event_name=event_name,
        event_type="s3_event"
    )


def log_transcribe_job(logger: structlog.BoundLogger, job_name: str, 
                      input_uri: str, output_bucket: str) -> None:
    """Log transcription job creation."""
    logger.info(
        "Transcription job created",
        job_name=job_name,
        input_uri=input_uri,
        output_bucket=output_bucket,
        event_type="transcribe_job_created"
    )


def log_transcribe_completion(logger: structlog.BoundLogger, job_name: str, 
                            status: str, output_location: str) -> None:
    """Log transcription job completion."""
    logger.info(
        "Transcription job completed",
        job_name=job_name,
        status=status,
        output_location=output_location,
        event_type="transcribe_job_completed"
    )


def log_error(logger: structlog.BoundLogger, error_type: str, error_message: str, 
              context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context."""
    log_data = {
        "error_type": error_type,
        "error_message": error_message,
        "event_type": "error"
    }
    
    if context:
        log_data.update(context)
    
    logger.error("Error occurred", **log_data)