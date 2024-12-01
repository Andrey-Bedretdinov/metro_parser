import logging
import os
import shutil
from datetime import datetime
from metro_parser.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def archive_log_file(log_file_path):
    """
    Архивирует существующий лог-файл, добавляя текущую дату к его имени.
    """
    if os.path.exists(log_file_path):
        # Формируем имя для архива
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_name = f"{log_file_path}.{timestamp}.bak"

        # Перемещаем текущий лог в архив
        shutil.move(log_file_path, archive_name)


def setup_logger(name="metro_parser"):
    """
    Создаёт и настраивает логгер.
    :param name: Имя логгера.
    :return: Настроенный объект логгера.
    """
    # Архивируем лог при каждом новом запуске
    archive_log_file(LOG_FILE)

    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Устанавливаем формат логов
    formatter = logging.Formatter(LOG_FORMAT)

    # Консольный обработчик (для вывода в терминал)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    # Обработчик для записи логов в файл
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики в логгер
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
