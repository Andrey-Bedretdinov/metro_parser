import aiohttp
import asyncio
from aiohttp import ClientResponseError, ClientConnectorError, ClientTimeout
from metro_parser.utils.logger import logger
from metro_parser.utils.file_handler import FileHandler
from metro_parser.config import HEADERS, TIMEOUT, REQUEST_DELAY, SAVE_HTML_RESPONSES
from datetime import datetime


class HTTPClient:
    def __init__(self):
        """
        Инициализация клиента с настройкой заголовков и тайм-аутов.
        """
        self.session = None
        self.timeout = ClientTimeout(total=TIMEOUT)

    async def __aenter__(self):
        """
        Контекстный менеджер для работы с клиентом.
        """
        self.session = aiohttp.ClientSession(headers=HEADERS, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Закрытие сессии при выходе из контекста.
        """
        if self.session:
            await self.session.close()

    async def fetch(self, url, retries=10, delay=REQUEST_DELAY):
        """
        Асинхронно получает HTML-контент страницы с обработкой ошибок и повторными попытками.

        :param url: URL для запроса.
        :param retries: Количество попыток в случае неудачи.
        :param delay: Задержка между повторными попытками.
        :return: HTML-контент страницы.
        """
        attempt = 0
        while attempt < retries:
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    content = await response.text()

                    if SAVE_HTML_RESPONSES:
                        FileHandler.save_response(content, response_id=self._get_response_id(url))

                    logger.info(f"Успешно загружена страница: {url}")
                    return content

            except (ClientResponseError, ClientConnectorError) as e:
                attempt += 1
                logger.error(f"Ошибка при запросе {url}: {str(e)} (попытка {attempt}/{retries})")
                if attempt < retries and delay:
                    await asyncio.sleep(delay)

            except asyncio.TimeoutError:
                logger.error(f"Тайм-аут запроса: {url} (попытка {attempt}/{retries})")
                attempt += 1
                if attempt < retries and delay:
                    await asyncio.sleep(delay)

        logger.critical(f"Не удалось загрузить страницу после {retries} попыток: {url}")
        raise Exception(f"Failed to fetch {url} after {retries} retries")

    @staticmethod
    def _get_response_id(url):
        """
        Генерирует идентификатор для файла HTML на основе URL.

        :param url: URL страницы.
        :return: Идентификатор файла (str).
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_url = url.replace("://", "_").replace("/", "_").replace("?", "_")
        return f"{safe_url}_{timestamp}"


# Тест
async def main():
    url = "https://online.metro-cc.ru/products/033l-sok-vinut-lichi-pryamoy-otzhim-zhb-216625"
    async with HTTPClient() as client:
        try:
            content = await client.fetch(url)
        except Exception as e:
            print(f"Ошибка при загрузке страницы {url}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
