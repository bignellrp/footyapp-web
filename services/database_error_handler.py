"""
Database Error Handler
Provides centralized error handling for database/API connectivity issues
"""
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
import logging

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database connectivity issues"""
    pass

def handle_api_request(func):
    """
    Decorator to handle API request errors gracefully
    Returns None when database is unreachable, allowing templates to show appropriate alerts
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ConnectionError, Timeout, RequestException) as e:
            logger.error(f"Database connection error in {func.__name__}: {str(e)}")
            raise DatabaseError(f"Database unreachable: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")
    return wrapper

def safe_api_call(api_function, default_return=None):
    """
    Safely call an API function and return default value if database is unreachable
    
    Args:
        api_function: Function to call
        default_return: Value to return if database is unreachable
    
    Returns:
        tuple: (success: bool, data: any, error_message: str)
    """
    try:
        result = api_function()
        return True, result, None
    except DatabaseError as e:
        return False, default_return, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in safe_api_call: {str(e)}")
        return False, default_return, f"Database error: {str(e)}"