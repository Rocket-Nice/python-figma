# main.py
import json
import os
from datetime import datetime
from figma_client import FigmaClient
from deep_analyzer import DeepFigmaAnalyzer
from smart_prompt_generator import SmartPromptGenerator
from config import Config

def main():
    print("🚀 Запуск УМНОЙ Figma-to-Code системы...")
    print(f"📁 File Key: {Config.FIGMA_FILE_KEY}")
    print(f"🎯 Target Node: {Config.FIGMA_NODE_ID}")
    
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # Инициализация компонентов
    figma_client = FigmaClient()
    deep_analyzer = DeepFigmaAnalyzer()
    smart_generator = SmartPromptGenerator()
    
    try:
        # Получаем данные из Figma
        figma_data = figma_client.get_full_structure()
        
        if not figma_data.get("full_file"):
            print("❌ Не удалось получить данные из Figma API")
            return
        
        # ПОЛНЫЙ анализ всей структуры
        print("🔍 Выполняем ПОЛНЫЙ анализ структуры...")
        complete_analysis = deep_analyzer.analyze_completely(figma_data)
        
        # Генерация умных промптов
        print("🧠 Генерируем УМНЫЕ промпты с разделением...")
        smart_generator.generate_smart_prompts(complete_analysis)
        
        # Выводим статистику
        stats = complete_analysis["statistics"]
        print(f"\n📊 ПОЛНАЯ СТАТИСТИКА:")
        print(f"   - Всего элементов: {stats['total_elements']}")
        print(f"   - Уровней вложенности: {stats['max_depth']}")
        print(f"   - Уникальных типов: {len(stats['type_counts'])}")
        
        print(f"\n🎯 УМНЫЕ ПРОМПТЫ СОЗДАНЫ!")
        print(f"📂 Папка: {Config.OUTPUT_DIR}/smart_prompts/")
        print(f"\n📋 СТРУКТУРА ПРОМПТОВ:")
        print(f"   📄 main_structure.txt - Основная структура")
        print(f"   📁 levels/ - Уровни вложенности (0-3)")
        print(f"   📁 element_types/ - Типы элементов")
        print(f"   📁 components/ - Сложные компоненты") 
        print(f"   📄 design_tokens.txt - Дизайн-система")
        print(f"   📄 SMART_INSTRUCTIONS.md - Инструкция")
        
        print(f"\n💡 СОВЕТ: Начни с main_structure.txt, затем используй остальные по необходимости")
        
    except Exception as e:
        print(f"💥 Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()