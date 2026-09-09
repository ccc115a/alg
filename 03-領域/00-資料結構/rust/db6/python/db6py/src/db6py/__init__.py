"""db6py - Python client for db6 database"""

from db6py.client import Client
from db6py.exceptions import Db6Error, ConnectionError, RequestError, ApiError

__version__ = "5.1.0"
__all__ = [
    "Client",
    "Db6Error",
    "ConnectionError",
    "RequestError",
    "ApiError",
]