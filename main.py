import asyncio
import os
from metro_parser.utils.logger import logger
from metro_parser.utils.file_handler import FileHandler
from metro_parser.parser import MetroParser
from metro_parser.config import BASE_URL, SAVE_HTML_RESPONSES, DATA_DIR, RESPONSES_DIR, LOGS_DIR, OUTPUT_DIR


def ensure_directories():
    """
    Создаёт все необходимые директории, если они не существуют.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESPONSES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


async def main():
    try:
        # Указываем категорию для парсинга
        category_url = f"{BASE_URL}/category/myasnye/myaso"
        logger.info(f"Запускаем парсер для категории: {category_url}")

        # Создаем экземпляр парсера
        parser = MetroParser(category_url)

        # Запускаем процесс парсинга
        await parser.run()

    except Exception as e:
        logger.error(f"Ошибка в процессе выполнения парсера: {e}")

    finally:
        if SAVE_HTML_RESPONSES:
            FileHandler.cleanup_responses()
            logger.info("Очистка старых HTML-ответов завершена.")


if __name__ == "__main__":
    # Создаем необходимые папки перед запуском
    ensure_directories()

    logger.info("Инициализация процесса парсинга.")
    asyncio.run(main())
    logger.info("Процесс парсинга завершён.")
