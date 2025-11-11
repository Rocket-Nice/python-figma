# figma_client.py
import requests
import json
from typing import Dict, Any
from config import Config

class FigmaClient:
    """
    Клиент для работы с Figma API
    Отвечает за получение данных из Figma
    """
    
    def __init__(self):
        # Инициализация с данными из конфига
        self.access_token = Config.FIGMA_ACCESS_TOKEN
        self.base_url = "https://api.figma.com/v1"  # Базовый URL Figma API
        self.headers = {"X-FIGMA-TOKEN": self.access_token}  # Заголовки для авторизации
    
    def get_file(self) -> Dict[str, Any]:
        """
        Получаем полную структуру файла Figma
        Возвращает JSON со всем содержимым файла
        """
        try:
            # Отправляем GET запрос к Figma API
            response = requests.get(
                f"{self.base_url}/files/{Config.FIGMA_FILE_KEY}",  # URL файла
                headers=self.headers,      # Заголовки с токеном
                timeout=30                 # Таймаут 30 секунд
            )
            response.raise_for_status()    # Проверяем статус ответа (если ошибка - исключение)
            return response.json()         # Возвращаем JSON ответ
        except requests.exceptions.RequestException as e:
            # Обрабатываем ошибки сети или API
            print(f"❌ Ошибка при запросе к Figma API: {e}")
            return {}  # Возвращаем пустой словарь при ошибке
    
    def get_specific_node(self) -> Dict[str, Any]:
        """
        Получаем конкретную ноду (элемент) по ID
        Полезно когда нужно анализировать не весь файл, а конкретный фрейм
        """
        try:
            # Запрос конкретной ноды по ID
            response = requests.get(
                f"{self.base_url}/files/{Config.FIGMA_FILE_KEY}/nodes?ids={Config.FIGMA_NODE_ID}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе конкретной ноды: {e}")
            return {}
    
    def get_full_structure(self) -> Dict[str, Any]:
        """
        Основной метод - получает полную структуру файла и конкретную ноду
        Возвращает объединенные данные для анализа
        """
        print("📡 Запрашиваем данные из Figma API...")
        
        # Получаем оба типа данных
        full_file = self.get_file()        # Весь файл
        specific_node = self.get_specific_node()  # Конкретная нода
        
        # Объединяем в одну структуру
        return {
            "full_file": full_file,        # Полная структура файла
            "specific_node": specific_node, # Данные конкретной ноды
            "target_node_id": Config.FIGMA_NODE_ID  # ID целевой ноды для отслеживания
        }