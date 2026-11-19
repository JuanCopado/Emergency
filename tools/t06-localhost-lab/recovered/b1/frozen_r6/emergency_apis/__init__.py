"""Isolated, read-only external evidence API prototype for Emergency.

No clinical recommendation or patient-data interface is provided.
"""

from .clients import APIClient, APIGatewayError, APIResult, NetworkDisabled, ValidationError

__all__ = ["APIClient", "APIGatewayError", "APIResult", "NetworkDisabled", "ValidationError"]
