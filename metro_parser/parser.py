import asyncio
from bs4 import BeautifulSoup
from metro_parser.utils.http_client import HTTPClient
from metro_parser.utils.file_handler import FileHandler
from metro_parser.utils.logger import logger
from metro_parser.config import BASE_URL, MAX_PAGES


class MetroParser:
    def __init__(self, category_url):
        """
        Инициализация парсера.
        :param category_url: URL категории товаров.
        """
        self.category_url = category_url
        self.products = []

    async def fetch_page(self, url):
        """
        Загружает HTML страницы по указанному URL.
        :param url: URL страницы.
        :return: HTML содержимое страницы.
        """
        logger.info(f"Загружаем страницу: {url}")
        async with HTTPClient() as client:
            try:
                html_content = await client.fetch(url)
                return html_content
            except Exception as e:
                logger.error(f"Ошибка загрузки страницы {url}: {e}")
                return None

    def parse_last_page(self, html_content):
        """
        Извлекает номер последней страницы.
        :param html_content: HTML содержимое страницы.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        pagination = soup.select("ul.catalog-paginate li a")  # Селектор для пагинации
        if pagination:
            self.last_page = max(int(link.text) for link in pagination if link.text.isdigit())
            logger.info(f"Найдено страниц: {self.last_page}")

        if MAX_PAGES and self.last_page > MAX_PAGES:
            self.last_page = MAX_PAGES
            logger.info(f"Ограничиваем количество страниц до: {self.last_page}")

    def parse_product_links(self, html_content):
        """
        Парсит ссылки на страницы товаров со страницы категории.
        :param html_content: HTML содержимое страницы.
        :return: Список ссылок на товары.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        product_cards = soup.select(".catalog-2-level-product-card a.product-card-name")
        links = [BASE_URL + card["href"] for card in product_cards if "href" in card.attrs]
        logger.info(f"Найдено товаров: {len(links)}")
        return links

    async def parse_product_page(self, url):
        """
        Парсит данные о товаре с его страницы.
        :param url: URL страницы товара.
        :return: Словарь с данными о товаре.
        """
        html_content = await self.fetch_page(url)
        if not html_content:
            logger.warning(f"Не удалось загрузить страницу товара: {url}")
            return None

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Название товара
            name_block = soup.select_one(".product-page-content__product-name")
            name = name_block.get_text(strip=True) if name_block else None

            # Артикул
            product_id_block = soup.select_one(".product-page-content__article")
            product_id = product_id_block.get_text(strip=True).replace("Артикул: ", "") if product_id_block else None

            # Бренд
            brand_block = soup.select_one(".product-attributes__list-item a[href*='/brand/']")
            brand = brand_block.get_text(strip=True) if brand_block else None

            # Цены
            prices = self.parse_prices(soup)

            if not prices:
                logger.warning(f"Цены не найдены на странице {url}")

            return {
                "id": product_id,
                "name": name,
                "brand": brand,
                **prices,
                "link": url,
            }
        except Exception as e:
            logger.error(f"Ошибка парсинга товара на странице {url}: {e}")
            return None

    @staticmethod
    def parse_prices(soup):
        """
        Извлекает цены с возможной скидкой.
        :param soup: Объект BeautifulSoup страницы товара.
        :return: Словарь с ценами.
        """

        def clean_price(price_text):
            """
            Очищает текст цены и преобразует в float.
            :param price_text: Строка с ценой.
            :return: float
            """
            if not price_text:
                return None
            price_text = price_text.replace("..", ".").strip()
            try:
                return float(price_text)
            except ValueError:
                return None

        try:
            # Актуальную цена
            current_price_block = soup.select_one(".product-unit-prices__actual-wrapper")
            current_price = None
            if current_price_block:
                rubles = current_price_block.select_one(".product-price__sum-rubles")
                pennies = current_price_block.select_one(".product-price__sum-penny")
                rubles = rubles.get_text(strip=True) if rubles else "0"
                pennies = pennies.get_text(strip=True) if pennies else "00"
                current_price = clean_price(f"{rubles}.{pennies}")

            # Старую цена
            old_price_block = soup.select_one(".product-unit-prices__old-wrapper")
            old_price = None
            if old_price_block:
                rubles = old_price_block.select_one(".product-price__sum-rubles")
                pennies = old_price_block.select_one(".product-price__sum-penny")
                rubles = rubles.get_text(strip=True) if rubles else "0"
                pennies = pennies.get_text(strip=True) if pennies else "00"
                old_price = clean_price(f"{rubles}.{pennies}")

            # Скидка
            discount_block = soup.select_one(".product-discount")
            discount = discount_block.get_text(strip=True) if discount_block else None

            # Цены в торговом центре
            offline_prices_block = soup.select_one(".product-page-prices-and-buttons__offline-bmpl-prices")
            offline_prices = []
            if offline_prices_block:
                for item in offline_prices_block.select(".product-prices-lines__item"):
                    actual_price_block = item.select_one(".product-range-prices__item-price-actual")
                    old_price_block = item.select_one(".product-prices-lines__item-price-old")
                    actual_price = None
                    old_price = None
                    if actual_price_block:
                        rubles = actual_price_block.select_one(".product-price__sum-rubles")
                        pennies = actual_price_block.select_one(".product-price__sum-penny")
                        rubles = rubles.get_text(strip=True) if rubles else "0"
                        pennies = pennies.get_text(strip=True) if pennies else "00"
                        actual_price = clean_price(f"{rubles}.{pennies}")
                    if old_price_block:
                        rubles = old_price_block.select_one(".product-price__sum-rubles")
                        pennies = old_price_block.select_one(".product-price__sum-penny")
                        rubles = rubles.get_text(strip=True) if rubles else "0"
                        pennies = pennies.get_text(strip=True) if pennies else "00"
                        old_price = clean_price(f"{rubles}.{pennies}")
                    offline_prices.append({"actual_price": actual_price, "old_price": old_price})

            return {
                "current_price": current_price,
                "old_price": old_price,
                "discount": discount,
                "offline_prices": offline_prices,
            }
        except Exception as e:
            print(f"Ошибка при извлечении цен: {e}")
            return {}

    async def run(self):
        """
        Запускает парсинг всех страниц категории и товаров.
        """
        logger.info(f"Начинаем парсинг категории: {self.category_url}")

        # Загружаем первую страницу категории
        first_page_content = await self.fetch_page(self.category_url)
        if not first_page_content:
            logger.error("Не удалось загрузить первую страницу.")
            return

        # Определяем количество страниц
        self.parse_last_page(first_page_content)

        # Сохраняем товары с первой страницы
        FileHandler.save_response(first_page_content, response_id="category_page_1")
        all_product_links = self.parse_product_links(first_page_content)

        # Создаем задачи для загрузки остальных страниц
        tasks = {
            page: asyncio.create_task(self.fetch_page(f"{self.category_url}?page={page}"))
            for page in range(2, self.last_page + 1)
        }

        # Асинхронно обрабатываем остальные страницы
        for page, task in tasks.items():
            try:
                page_content = await task
                if not page_content:
                    logger.warning(f"Не удалось загрузить страницу {page}. Пропускаем.")
                    continue

                # Сохраняем ответ и парсим товары со страницы
                FileHandler.save_response(page_content, response_id=f"category_page_{page}")
                product_links = self.parse_product_links(page_content)
                logger.info(f"Найдено {len(product_links)} товаров на странице {page}.")
                all_product_links.extend(product_links)
            except Exception as e:
                logger.error(f"Ошибка при обработке страницы {page}: {e}")

        # Убираем дубликаты ссылок (если это актуально)
        all_product_links = list(set(all_product_links))

        # Парсим все найденные товары
        product_tasks = [self.parse_product_page(link) for link in all_product_links]
        results = await asyncio.gather(*product_tasks, return_exceptions=True)

        # Фильтруем успешные результаты
        self.products = [result for result in results if isinstance(result, dict)]

        FileHandler.save_json(self.products)

        # Завершение процесса
        logger.info(f"Парсинг завершён успешно. Найдено товаров: {len(self.products)}")


if __name__ == "__main__":
    category_url = f"{BASE_URL}/category/bezalkogolnye-napitki/soki-morsy-nektary"
    parser = MetroParser(category_url)
    asyncio.run(parser.run())
