import os

# Базовый URL сайта
BASE_URL = "https://online.metro-cc.ru"

# Тайм-аут для запросов (в секундах)
TIMEOUT = 30

# Заголовки для HTTP-запросов
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Папка для данных
DATA_DIR = os.path.join(BASE_DIR, "data")

# Папка для логов
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")

# Путь для сохранения итогового JSON
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.json")

# Папка для HTML-ответов
RESPONSES_DIR = os.path.join(DATA_DIR, "responses")

# Папка для логов
LOGS_DIR = os.path.join(DATA_DIR, "logs")

# Путь для файла логов
LOG_FILE = os.path.join(LOGS_DIR, "parser.log")


# Уровень логирования
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Формат логирования
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


# Сохранять ли HTML-ответы
SAVE_HTML_RESPONSES = False

# Максимальное количество страниц для парсинга
MAX_PAGES = 100  # None для бесконечного парсинга, пока есть страницы

# Задержка между запросами (в секундах)
REQUEST_DELAY = 10  # None для отсутствия задержек
