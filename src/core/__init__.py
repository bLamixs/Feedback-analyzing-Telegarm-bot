"""
Ядро приложения: оркестратор, модели данных и исключения.

Содержит основные компоненты для координации работы всех сервисов бота.
"""

from .orchestrator import Orchestrator
from .exceptions import OrchestratorError, ProcessingError, ServiceUnavailableError
from .models import UserContext, ProcessedMessage

__all__ = [
    # Основной класс
    "Orchestrator",

    # Модели данных
    "UserContext",
    "ProcessedMessage",

    # Исключения
    "OrchestratorError",
    "ProcessingError",
    "ServiceUnavailableError",
]