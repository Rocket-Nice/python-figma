# AI Agent (выбери один)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")  # Для GPT
# или OLLAMA_URL = "http://localhost:11434"  # Для локальной модели

# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    # Ваши данные Figma из .env файла
    FIGMA_ACCESS_TOKEN = os.getenv('FIGMA_ACCESS_TOKEN')
    FIGMA_FILE_KEY = os.getenv('FIGMA_FILE_KEY')
    
    # Исправляем node-id - в API используется двоеточие, а в URL дефис
    FIGMA_NODE_ID = "1619:4"  # Меняем дефис на двоеточие!
    
    # Для Copilot/VS Code
    OUTPUT_DIR = "generated_code"
    
    # Настройки разделения
    MAX_ELEMENTS_PER_FRAME = 200  # Максимум элементов в одном фрейме (но сохраняем полную вложенность)
    MIN_FRAME_CHILDREN = 2  # Минимальное количество детей для создания отдельного промпта фрейма

    # Константы анализа
    SPACING_BASE = 8