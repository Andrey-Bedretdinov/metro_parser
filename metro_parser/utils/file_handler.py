import os
import json
from datetime import datetime
import shutil
from metro_parser.config import OUTPUT_FILE, RESPONSES_DIR, SAVE_HTML_RESPONSES


class FileHandler:
    @staticmethod
    def save_json(data, filepath=OUTPUT_FILE, archive=True):
        """
        Сохраняет данные в JSON-файл. При необходимости архивирует предыдущую версию.

        :param data: Данные для сохранения (dict или list).
        :param filepath: Путь к файлу для сохранения.
        :param archive: Флаг, указывающий, нужно ли архивировать старый файл.
        """
        if archive and os.path.exists(filepath):
            FileHandler._archive_file(filepath)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def read_json(filepath=OUTPUT_FILE):
        """
        Читает JSON-файл и возвращает его содержимое.

        :param filepath: Путь к файлу.
        :return: Содержимое JSON-файла (dict или list).
        """
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_response(content, response_id=None):
        """
        Сохраняет HTML-ответ в файл, если включено сохранение.

        :param content: HTML-строка.
        :param response_id: Идентификатор или метка для файла (например, URL или номер страницы).
        """
        if not SAVE_HTML_RESPONSES:
            return

        if not response_id:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            response_id = f"response_{timestamp}"

        filename = os.path.join(RESPONSES_DIR, f"{response_id}.html")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def cleanup_responses(retention_days=3):
        """
        Удаляет HTML-файлы старше заданного количества дней.

        :param retention_days: Срок хранения файлов в днях.
        """
        now = datetime.now()

        for file_name in os.listdir(RESPONSES_DIR):
            file_path = os.path.join(RESPONSES_DIR, file_name)
            if os.path.isfile(file_path):
                file_age = (now - datetime.fromtimestamp(os.path.getmtime(file_path))).days
                if file_age > retention_days:
                    os.remove(file_path)

    @staticmethod
    def _archive_file(filepath):
        """
        Перемещает файл в архив, добавляя метку времени к имени.

        :param filepath: Путь к файлу для архивирования.
        """
        archive_dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_name = os.path.join(archive_dir, f"{filename}.{timestamp}.bak")
        shutil.move(filepath, archive_name)

    @staticmethod
    def file_exists(filepath):
        """
        Проверяет, существует ли файл.

        :param filepath: Путь к файлу.
        :return: True, если файл существует, иначе False.
        """
        return os.path.exists(filepath)

    @staticmethod
    def read_file(filepath):
        """
        Читает содержимое файла и возвращает его в виде строки.

        :param filepath: Путь к файлу.
        :return: Содержимое файла как строка.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
