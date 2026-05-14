"""
Storage Service — модуль для работы с базой данных.
"""

from .storage_service import StorageService
from .exceptions import StorageError, UserNotFoundError, MessageNotFoundError
from .database import init_db, close_db

__all__ = [
    "StorageService",
    "StorageError",
    "UserNotFoundError",
    "MessageNotFoundError",
    "init_db",
    "close_db",
]