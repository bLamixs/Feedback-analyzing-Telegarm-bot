"""
Специфичные исключения для оркестратора.
"""

class OrchestratorError(Exception):
    """Базовое исключение оркестратора"""
    pass

class ProcessingError(OrchestratorError):
    """Ошибка при обработке сообщения"""
    pass

class ServiceUnavailableError(OrchestratorError):
    """Один из сервисов недоступен"""
    pass