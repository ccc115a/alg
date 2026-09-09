"""db6py exceptions"""


class Db6Error(Exception):
    """Base exception for db6py"""
    pass


class ConnectionError(Db6Error):
    """Connection to db6 server failed"""
    pass


class RequestError(Db6Error):
    """Request to db6 server failed"""
    pass


class ApiError(Db6Error):
    """db6 API returned an error"""
    pass