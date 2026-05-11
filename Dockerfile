FROM python:3.11-slim as base

# Устанавливаем системные зависимости для аудио и БД
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry (опционально) или pip
# Для простоты используем pip, но можно перейти на poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Копируем только файлы зависимостей (для кэширования слоёв)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================
# STAGE 2: Финальный образ
# ============================================
FROM python:3.11-slim

# Копируем системные библиотеки из первого этапа
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=base /usr/lib/*/libsndfile* /usr/lib/

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем весь код
COPY . .

# Создаём папки для данных
RUN mkdir -p /app/data/audio /app/data/logs

# Команда запуска
CMD ["python", "main.py"]