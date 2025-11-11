# frame_splitter.py
import json
import os
from typing import Dict, Any, List, Tuple
from config import Config

class FrameSplitter:
    """
    Разделитель больших Figma макетов на логические фреймы
    Превращает один огромный макет на управляемые секции
    """
    
    def __init__(self):
        # Настройки путей для выходных файлов
        self.output_dir = Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)  # Создаем папку если нет
        
        # Папка для отдельных фреймов
        self.frames_dir = os.path.join(self.output_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)
        
        self.frames_count = 0  # Счетчик созданных фреймов
    
    def split_into_frames(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод - разделяет анализ на родительские фреймы первого уровня
        Сохраняет ПОЛНУЮ ВЛОЖЕННОСТЬ каждого фрейма
        """
        print("🔄 Разделяем структуру на родительские фреймы первого уровня...")
        
        # Структура для хранения данных о всех фреймах
        frames_data = {
            "root_frame": None,      # Главный фрейм (весь макет)
            "parent_frames": [],     # Только родительские фреймы первого уровня (основные секции)
            "total_frames": 0,       # Общее количество фреймов
            "frame_map": {}          # Словарь для быстрого доступа к фреймам по ID
        }
        
        # Получаем корневой элемент из анализа
        root_element = analysis["target_node"]
        
        # Сохраняем корневой фрейм (С ПОЛНОЙ ВЛОЖЕННОСТЬЮ всех элементов)
        root_frame_data = self._extract_frame_data(root_element, "root", analysis["design_tokens"])
        frames_data["root_frame"] = root_frame_data
        frames_data["frame_map"]["root"] = root_frame_data
        self.frames_count += 1
        
        # Логируем информацию о корневом фрейме
        total_elements_in_root = self._count_total_elements(root_element)
        print(f"   📦 Корневой фрейм: {root_element.get('name')} -> {total_elements_in_root} элементов")
        
        # Находим и сохраняем только родительские фреймы первого уровня
        # Это основные секции макета: header, main, footer, sidebar и т.д.
        self._find_and_save_parent_frames(root_element, frames_data, analysis["design_tokens"])
        
        frames_data["total_frames"] = self.frames_count
        
        # Сохраняем мета-информацию о всех фреймах
        self._save_frames_metadata(frames_data)
        
        print(f"✅ Разделение завершено! Всего фреймов: {frames_data['total_frames']}")
        return frames_data
    
    def _find_and_save_parent_frames(self, root_element: Dict[str, Any], 
                                   frames_data: Dict[str, Any], design_tokens: Dict[str, Any]):
        """
        Находит и сохраняет только родительские фреймы первого уровня
        Это основные логические блоки макета
        """
        children = root_element.get("children", [])
        
        print(f"🔍 Ищем родительские фреймы первого уровня...")
        
        # Проходим по всем детям корневого элемента
        for child in children:
            child_type = child.get("type", "")
            child_name = child.get("name", "unnamed")
            child_id = child.get("id", "").split("-")[0]  # Берем первую часть ID
            
            # Берем только FRAME элементы первого уровня (основные секции)
            if child_type == "FRAME":
                # Извлекаем данные фрейма (С ПОЛНОЙ ВЛОЖЕННОСТЬЮ всех детей)
                frame_data = self._extract_frame_data(child, child_id, design_tokens)
                frame_data["parent"] = "root"  # Отмечаем что родитель - корневой фрейм
                
                # Сохраняем фрейм в отдельный JSON файл
                self._save_single_frame(frame_data)
                
                # Считаем общее количество элементов во фрейме (включая вложенные)
                total_elements = self._count_total_elements(child)
                
                # Добавляем информацию о фрейме в общую структуру
                frames_data["parent_frames"].append({
                    "id": child_id,
                    "name": child_name,
                    "element_count": len(child.get("children", [])),  # Только непосредственные дети
                    "total_elements": total_elements,  # Все элементы включая вложенные
                    "file": f"frames/{child_id}_{self._sanitize_name(child_name)}.json"  # Путь к файлу
                })
                
                # Добавляем в карту фреймов для быстрого доступа
                frames_data["frame_map"][child_id] = frame_data
                self.frames_count += 1
                
                # Логируем информацию о фрейме
                print(f"   📦 Родительский фрейм '{child_name}' -> {total_elements} элементов (включая вложенные)")
    
    def _extract_frame_data(self, frame_element: Dict[str, Any], frame_id: str, design_tokens: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает данные для отдельного фрейма с ПОЛНОЙ ВЛОЖЕННОСТЬЮ
        Сохраняет всех детей, детей детей и т.д.
        """
        return {
            "id": frame_id,
            "name": frame_element.get("name", ""),
            "type": frame_element.get("type", ""),
            "size": frame_element.get("size", {}),        # Размеры фрейма
            "position": frame_element.get("position", {}), # Позиция относительно родителя
            "styles": frame_element.get("styles", {}),    # Стили фрейма
            "layout": frame_element.get("layout", {}),    # Настройки лайаута
            "children": frame_element.get("children", []),  # ВАЖНО: СОХРАНЯЕМ ПОЛНУЮ ВЛОЖЕННОСТЬ
            "element_count": len(frame_element.get("children", [])),  # Количество непосредственных детей
            "total_elements": self._count_total_elements(frame_element),  # Всего элементов включая вложенные
            "design_tokens": self._extract_frame_design_tokens(frame_element),  # Токены используемые в этом фрейме
            "global_design_tokens": {  # Глобальные токены всего макета (первые несколько)
                "colors": dict(list(design_tokens.get("colors", {}).items())[:10]),      # Первые 10 цветов
                "typography": dict(list(design_tokens.get("typography", {}).items())[:5]), # Первые 5 стилей шрифтов
                "spacing": dict(list(design_tokens.get("spacing", {}).items())[:5]),     # Первые 5 отступов
                "border_radius": dict(list(design_tokens.get("border_radius", {}).items())[:5])  # Первые 5 скруглений
            }
        }
    
    def _count_total_elements(self, element: Dict[str, Any]) -> int:
        """
        Рекурсивно считает общее количество элементов включая всех детей
        Используется для оценки сложности фрейма
        """
        count = 1  # Начинаем с текущего элемента
        
        # Рекурсивно добавляем счетчики всех детей
        for child in element.get("children", []):
            count += self._count_total_elements(child)
        
        return count
    
    def _extract_frame_design_tokens(self, frame_element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает дизайн-токены, используемые только в этом фрейме
        Помогает понять какие цвета/шрифты/отступы используются в каждой секции
        """
        colors = set()
        typography_styles = []
        spacing_values = set()
        radius_values = set()
        
        def collect_tokens(element: Dict[str, Any]):
            """
            Внутренняя рекурсивная функция для сбора токенов
            """
            # Собираем цвета из разных мест элемента
            bg_color = element.get("styles", {}).get("background")
            if bg_color:
                colors.add(bg_color)
            
            border_color = element.get("styles", {}).get("border", {}).get("color")
            if border_color:
                colors.add(border_color)
            
            text_color = element.get("styles", {}).get("typography", {}).get("color")
            if text_color:
                colors.add(text_color)
            
            # Собираем типографику
            typo = element.get("styles", {}).get("typography", {})
            if typo and any(typo.values()):  # Если есть хоть какие-то данные о шрифтах
                typography_styles.append(typo)
            
            # Собираем значения отступов и промежутков
            layout = element.get("layout", {})
            spacing = layout.get("spacing", 0)  # Расстояние между элементами
            if spacing > 0:
                spacing_values.add(spacing)
            
            # Собираем padding (внутренние отступы)
            padding = layout.get("padding", {})
            for key in ["left", "right", "top", "bottom"]:
                padding_val = padding.get(key, 0)
                if padding_val > 0:
                    spacing_values.add(padding_val)
            
            # Собираем border radius (скругления)
            border_radius = element.get("styles", {}).get("border", {}).get("radius", 0)
            if border_radius > 0:
                radius_values.add(border_radius)
            
            # Рекурсивно обрабатываем всех детей
            for child in element.get("children", []):
                collect_tokens(child)
        
        # Запускаем сбор токенов для этого фрейма и всех его детей
        collect_tokens(frame_element)
        
        return {
            "colors": list(colors),           # Уникальные цвета в этом фрейме
            "typography": typography_styles,  # Стили шрифтов
            "spacing": sorted(list(spacing_values)),      # Отсортированные значения отступов
            "border_radius": sorted(list(radius_values))  # Отсортированные значения скруглений
        }
    
    def _save_single_frame(self, frame_data: Dict[str, Any]):
        """
        Сохраняет отдельный фрейм в JSON файл
        """
        # Создаем безопасное имя файла из ID и имени фрейма
        filename = f"{frame_data['id']}_{self._sanitize_name(frame_data['name'])}.json"
        filepath = os.path.join(self.frames_dir, filename)
        
        # Сохраняем в JSON с красивым форматированием
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _save_frames_metadata(self, frames_data: Dict[str, Any]):
        """
        Сохраняет мета-информацию о всех фреймах
        Это как оглавление для всей системы фреймов
        """
        # Структура метаданных
        metadata = {
            "root_frame": {
                "name": frames_data["root_frame"]["name"],
                "element_count": frames_data["root_frame"]["element_count"],
                "total_elements": frames_data["root_frame"]["total_elements"],
                "file": "root_frame.json"  # Файл корневого фрейма
            },
            "parent_frames": frames_data["parent_frames"],  # Список родительских фреймов
            "total_frames": frames_data["total_frames"]     # Общее количество
        }
        
        # Сохраняем корневой фрейм в отдельный файл
        root_filepath = os.path.join(self.frames_dir, "root_frame.json")
        with open(root_filepath, "w", encoding="utf-8") as f:
            json.dump(frames_data["root_frame"], f, indent=2, ensure_ascii=False, default=str)
        
        # Сохраняем метаданные в отдельный файл
        meta_filepath = os.path.join(self.output_dir, "frames_metadata.json")
        with open(meta_filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        # Создаем удобный индекс для навигации по фреймам
        self._create_frames_index(metadata)
    
    def _create_frames_index(self, metadata: Dict[str, Any]):
        """
        Создает красивый Markdown файл с индексом всех фреймов
        Помогает быстро понять структуру макета
        """
        index_content = f"""
# ИНДЕКС ФРЕЙМОВ (РОДИТЕЛЬСКИЕ ФРЕЙМЫ ПЕРВОГО УРОВНЯ)

## КОРНЕВОЙ ФРЕЙМ:
- **{metadata['root_frame']['name']}** 
  - Элементов: {metadata['root_frame']['element_count']}
  - Всего с вложенными: {metadata['root_frame']['total_elements']}
  - Файл: `{metadata['root_frame']['file']}`

## РОДИТЕЛЬСКИЕ ФРЕЙМЫ ПЕРВОГО УРОВНЯ ({len(metadata['parent_frames'])} шт):
{self._format_parent_frames_list(metadata['parent_frames'])}

## ИНСТРУКЦИЯ:
1. Каждый фрейм содержит ПОЛНУЮ ВЛОЖЕННОСТЬ своих элементов
2. Начни с корневого фрейма (root_frame.json) для общей структуры
3. Затем реализуй родительские фреймы по одному
4. Все элементы сохраняют свои детей, детей детей и т.д.
5. Каждый JSON файл самодостаточен

## ПРЕИМУЩЕСТВА:
- ✅ Только основные секции макета
- ✅ Каждый промпт самодостаточен
- ✅ Не нужно собирать элементы из разных файлов
- ✅ Сохранены все связи и вложенности
- ✅ Легко реализовать любую секцию целиком

## СТРУКТУРА МАКЕТА:
Корневой фрейм содержит {metadata['root_frame']['total_elements']} элементов.
Родительские фреймы первого уровня разделяют макет на основные секции.
"""
        
        # Сохраняем индекс в Markdown файл
        index_filepath = os.path.join(self.frames_dir, "FRAMES_INDEX.md")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
    
    def _format_parent_frames_list(self, frames: List[Dict[str, Any]]) -> str:
        """
        Форматирует список родительских фреймов в красивый Markdown
        """
        lines = []
        for frame in frames:
            lines.append(f"- **{frame['name']}**")
            lines.append(f"  - ID: `{frame['id']}`")
            lines.append(f"  - Элементов: {frame['element_count']}")
            lines.append(f"  - Всего с вложенными: {frame['total_elements']}")
            lines.append(f"  - Файл: `{frame['file']}`")
            lines.append("")  # Пустая строка между фреймами
        
        return "\n".join(lines)
    
    def _sanitize_name(self, name: str) -> str:
        """
        Очищает имя для использования в имени файла
        Убирает специальные символы, оставляет только буквы и цифры
        """
        return "".join(c if c.isalnum() else "_" for c in name.lower())[:30]  # Ограничиваем длину