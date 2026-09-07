from enum import Enum
from openai import OpenAIError, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError, InternalServerError, BadRequestError
import anthropic
# Anthropic exceptions might need specific import depending on version
# In 1.4.0, they are under anthropic.BadRequestError etc.

class APIStatus(Enum):
    SUCCESS = "SUCCESS"
    RETRYABLE_ERROR = "RETRYABLE_ERROR"
    CREDIT_EXHAUSTED = "CREDIT_EXHAUSTED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    API_ERROR = "API_ERROR"

def classify_error(e):
    error_str = str(e).lower()
    
    # 400 Bad Request (not retryable)
    if isinstance(e, (BadRequestError, anthropic.BadRequestError)):
        return APIStatus.API_ERROR
        
    # Authentication / Configuration
    if isinstance(e, (AuthenticationError, anthropic.AuthenticationError)):
        return APIStatus.CONFIGURATION_ERROR
    
    # Check for quota/credit issues
    if "insufficient_quota" in error_str or "credit" in error_str or "billing" in error_str or "exceeded_quota" in error_str:
        return APIStatus.CREDIT_EXHAUSTED
    
    # Rate Limit
    if isinstance(e, (RateLimitError, anthropic.RateLimitError)):
        return APIStatus.RETRYABLE_ERROR
        
    # Timeout/Connection/Server (Retryable)
    if isinstance(e, (APITimeoutError, APIConnectionError, anthropic.APIConnectionError, InternalServerError, anthropic.InternalServerError)):
        return APIStatus.RETRYABLE_ERROR
    
    # Fallback
    return APIStatus.API_ERROR
