# AI Agent (выбери один)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")  # Для GPT
# или OLLAMA_URL = "http://localhost:11434"  # Для локальной модели

# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    # Конфигурация Figma API
    # Эти данные берутся из переменных окружения или .env файла
    FIGMA_ACCESS_TOKEN = os.getenv('FIGMA_ACCESS_TOKEN')  # Токен для доступа к Figma API
    FIGMA_FILE_KEY = os.getenv('FIGMA_FILE_KEY')          # ID файла Figma (из URL)
    
    # ID конкретной ноды (элемента) для анализа
    # В Figma API используется двоеточие, в URL - дефис, поэтому меняем
    FIGMA_NODE_ID = "96:5321"  # Пример: "1619:4" вместо "1619-4"
    
    # Настройки выходных файлов
    OUTPUT_DIR = "generated_code"  # Папка куда сохраняем результаты
    
    # Настройки для разделения больших макетов
    MAX_ELEMENTS_PER_FRAME = 200  # Если элементов больше - разбиваем на части
    MIN_FRAME_CHILDREN = 2        # Минимальное количество детей для создания отдельного фрейма
    
    # Базовые значения для анализа (используются для нормализации)
    SPACING_BASE = 8  # Базовый шаг отступов (часто 8px система)