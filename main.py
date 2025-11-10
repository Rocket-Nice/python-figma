# main.py
import json
import os
from datetime import datetime
from figma_client import FigmaClient
from deep_analyzer import DeepFigmaAnalyzer
from smart_prompt_generator import SmartPromptGenerator
from frame_splitter import FrameSplitter
from config import Config

def main():
    print("🚀 Запуск Figma-to-Code системы с РОДИТЕЛЬСКИМИ ФРЕЙМАМИ...")
    print(f"📁 File Key: {Config.FIGMA_FILE_KEY}")
    print(f"🎯 Target Node: {Config.FIGMA_NODE_ID}")
    
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # Инициализация компонентов
    figma_client = FigmaClient()
    deep_analyzer = DeepFigmaAnalyzer()
    smart_generator = SmartPromptGenerator()
    frame_splitter = FrameSplitter()
    
    try:
        # Получаем данные из Figma
        figma_data = figma_client.get_full_structure()
        
        if not figma_data.get("full_file"):
            print("❌ Не удалось получить данные из Figma API")
            return
        
        # ПОЛНЫЙ анализ всей структуры
        print("🔍 Выполняем ПОЛНЫЙ анализ структуры...")
        complete_analysis = deep_analyzer.analyze_completely(figma_data)
        
        # РАЗДЕЛЯЕМ на родительские фреймы первого уровня
        print("🔄 Разделяем структуру на родительские фреймы первого уровня...")
        frames_data = frame_splitter.split_into_frames(complete_analysis)
        
        # Генерация умных промптов для каждого фрейма
        print("🧠 Генерируем УМНЫЕ промпты для каждого фрейма...")
        smart_generator.generate_smart_prompts(complete_analysis, frames_data)
        
        # Выводим статистику
        stats = complete_analysis["statistics"]
        print(f"\n📊 ПОЛНАЯ СТАТИСТИКА:")
        print(f"   - Всего элементов: {stats['total_elements']}")
        print(f"   - Уровней вложенности: {stats['max_depth']}")
        print(f"   - Уникальных типов: {len(stats['type_counts'])}")
        print(f"   - Всего фреймов: {frames_data['total_frames']}")
        print(f"   - Родительских фреймов: {len(frames_data['parent_frames'])}")
        
        print(f"\n🎯 СИСТЕМА РАЗДЕЛЕНА НА РОДИТЕЛЬСКИЕ ФРЕЙМЫ!")
        print(f"📂 Папка: {Config.OUTPUT_DIR}/")
        print(f"\n📋 СТРУКТУРА ВЫХОДНЫХ ФАЙЛОВ:")
        print(f"   📄 frames/root_frame.json - Корневой фрейм")
        print(f"   📁 frames/ - Родительские фреймы ({len(frames_data['parent_frames'])} шт)")
        print(f"   📄 frames_metadata.json - Метаданные фреймов")
        print(f"   📄 FRAMES_INDEX.md - Навигация по фреймам")
        print(f"   📁 smart_prompts/ - Умные промпты")
        print(f"   📄 complete_analysis_full.json - Полный анализ")
        
        print(f"\n💡 КЛЮЧЕВЫЕ ПРЕИМУЩЕСТВА:")
        print(f"   ✅ Только основные секции макета ({len(frames_data['parent_frames'])} фреймов)")
        print(f"   ✅ Каждый фрейм содержит ПОЛНУЮ ВЛОЖЕННОСТЬ своих элементов")
        print(f"   ✅ Логическое разделение на управляемое количество компонентов")
        print(f"   ✅ Можно реализовать каждую секцию целиком по одному промпту")
        
        print(f"\n🚀 СОВЕТ ПО ИСПОЛЬЗОВАНИЮ:")
        print(f"   1. Начни с smart_prompts/root_frame_prompt.txt")
        print(f"   2. Затем реализуй секции из smart_prompts/parent_frames/")
        print(f"   3. Каждый промпт самодостаточен - содержит всю структуру секции")
        print(f"   4. Интегрируй готовые секции в корневую структуру")
        
        # Показываем список родительских фреймов
        if frames_data['parent_frames']:
            print(f"\n📋 СПИСОК РОДИТЕЛЬСКИХ ФРЕЙМОВ:")
            for i, frame in enumerate(frames_data['parent_frames'][:10]):  # Показываем первые 10
                print(f"   {i+1}. {frame['name']} ({frame['total_elements']} элементов)")
            if len(frames_data['parent_frames']) > 10:
                print(f"   ... и еще {len(frames_data['parent_frames']) - 10} фреймов")
        
    except Exception as e:
        print(f"💥 Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()