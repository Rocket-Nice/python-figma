# figma_client.py
import requests
import json
from typing import Dict, Any
from config import Config

class FigmaClient:
    def __init__(self):
        self.access_token = Config.FIGMA_ACCESS_TOKEN
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-FIGMA-TOKEN": self.access_token}
    
    def get_file(self) -> Dict[str, Any]:
        """Получаем полную структуру файла Figma"""
        try:
            response = requests.get(
                f"{self.base_url}/files/{Config.FIGMA_FILE_KEY}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе к Figma API: {e}")
            return {}
    
    def get_specific_node(self) -> Dict[str, Any]:
        """Получаем конкретную ноду по ID"""
        try:
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
        """Получаем полную структуру и конкретную ноду"""
        print("📡 Запрашиваем данные из Figma API...")
        full_file = self.get_file()
        specific_node = self.get_specific_node()
        
        return {
            "full_file": full_file,
            "specific_node": specific_node,
            "target_node_id": Config.FIGMA_NODE_ID
        }