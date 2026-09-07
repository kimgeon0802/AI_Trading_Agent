from enum import Enum
from openai import OpenAIError, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError, InternalServerError
from anthropic import APIError, AuthenticationError as AnthropicAuthError, RateLimitError as AnthropicRateLimitError, APIConnectionError as AnthropicConnError, InternalServerError as AnthropicInternalError

class APIStatus(Enum):
    SUCCESS = "SUCCESS"
    RETRYABLE_ERROR = "RETRYABLE_ERROR"
    CREDIT_EXHAUSTED = "CREDIT_EXHAUSTED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    API_ERROR = "API_ERROR"

def classify_error(e):
    # Anthropic/OpenAI specific classification
    if isinstance(e, (AuthenticationError, AnthropicAuthError)):
        return APIStatus.CONFIGURATION_ERROR
    
    # Check for quota/credit issues (often mapped to specific status codes or messages)
    error_str = str(e).lower()
    if "insufficient_quota" in error_str or "credit" in error_str or "billing" in error_str or "exceeded_quota" in error_str:
        return APIStatus.CREDIT_EXHAUSTED
    
    if isinstance(e, (RateLimitError, AnthropicRateLimitError)):
        return APIStatus.RETRYABLE_ERROR
        
    if isinstance(e, (APITimeoutError, APIConnectionError, AnthropicConnError, InternalServerError, AnthropicInternalError)):
        return APIStatus.RETRYABLE_ERROR
    
    return APIStatus.API_ERROR
