"""
Исключения для модуля хранения данных.
"""

class StorageError(Exception):
    """Базовое исключение для всех ошибок хранилища"""
    pass

class DatabaseConnectionError(StorageError):
    """Ошибка подключения к базе данных"""
    pass

class UserNotFoundError(StorageError):
    """Пользователь не найден в БД"""
    pass

class MessageNotFoundError(StorageError):
    """Сообщение не найдено в БД"""
    pass

class SaveError(StorageError):
    """Ошибка при сохранении данных"""
    pass