"""
Exceptions for the UniFi API Client
"""

class UniFiAPIError(Exception):
    """Base exception for UniFi API errors"""
    pass

class CurlGeneralErrorException(UniFiAPIError):
    """Raised when a general request error occurs"""
    pass

class CurlTimeoutException(UniFiAPIError):
    """Raised when a request times out"""
    pass

class EmailInvalidException(UniFiAPIError):
    """Raised when an invalid email is provided"""
    pass

class InvalidBaseUrlException(UniFiAPIError):
    """Raised when the base URL is invalid"""
    pass

class InvalidMethodException(UniFiAPIError):
    """Raised when an invalid HTTP method is used"""
    pass

class InvalidSiteNameException(UniFiAPIError):
    """Raised when an invalid site name is provided"""
    pass

class JsonDecodeException(UniFiAPIError):
    """Raised when JSON decoding fails"""
    pass

class LoginFailedException(UniFiAPIError):
    """Raised when login fails"""
    pass

class LoginRequiredException(UniFiAPIError):
    """Raised when an API call is made without being logged in"""
    pass

class MethodDeprecatedException(UniFiAPIError):
    """Raised when a deprecated method is called"""
    pass
