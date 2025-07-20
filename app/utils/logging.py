import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from DatabaseManager import  DatabaseManager
import datetime

class ApplicationLogger:
    """
    Custom logger class to handle application logging
    Logs to both file and database
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def log_request(self, endpoint: str, method: str, status_code: int,
                    message: str, additional_data: Dict[str, Any] = None):
        """
        Log application request to database

        Args:
            endpoint: API endpoint that was called
            method: HTTP method used
            status_code: HTTP response status code
            message: Log message
            additional_data: Additional data to include in log
        """
        try:
            log_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'message': message,
                'additional_data': additional_data or {}
            }

            self.db_manager.insert_log_record(log_record)
        except Exception as e:
            # Don't let logging errors break the application
            logging.error(f"Failed to log request to database: {e}")
