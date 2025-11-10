# frame_splitter.py
import json
import os
from typing import Dict, Any, List, Tuple
from config import Config

class FrameSplitter:
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.frames_dir = os.path.join(self.output_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)
        self.frames_count = 0
    
    def split_into_frames(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Разделяем анализ на родительские фреймы первого уровня с ПОЛНОЙ ВЛОЖЕННОСТЬЮ"""
        print("🔄 Разделяем структуру на родительские фреймы первого уровня...")
        
        frames_data = {
            "root_frame": None,
            "parent_frames": [],  # Только родительские фреймы первого уровня
            "total_frames": 0,
            "frame_map": {}
        }
        
        root_element = analysis["target_node"]
        
        # Сохраняем корневой фрейм (С ПОЛНОЙ ВЛОЖЕННОСТЬЮ)
        root_frame_data = self._extract_frame_data(root_element, "root", analysis["design_tokens"])
        frames_data["root_frame"] = root_frame_data
        frames_data["frame_map"]["root"] = root_frame_data
        self.frames_count += 1
        
        print(f"   📦 Корневой фрейм: {root_element.get('name')} -> {self._count_total_elements(root_element)} элементов")
        
        # Находим и сохраняем только родительские фреймы первого уровня
        self._find_and_save_parent_frames(root_element, frames_data, analysis["design_tokens"])
        
        frames_data["total_frames"] = self.frames_count
        
        # Сохраняем мета-информацию о фреймах
        self._save_frames_metadata(frames_data)
        
        print(f"✅ Разделение завершено! Всего фреймов: {frames_data['total_frames']}")
        return frames_data
    
    def _find_and_save_parent_frames(self, root_element: Dict[str, Any], 
                                   frames_data: Dict[str, Any], design_tokens: Dict[str, Any]):
        """Находим и сохраняем только родительские фреймы первого уровня"""
        children = root_element.get("children", [])
        
        print(f"🔍 Ищем родительские фреймы первого уровня...")
        
        for child in children:
            child_type = child.get("type", "")
            child_name = child.get("name", "unnamed")
            child_id = child.get("id", "").split("-")[0]
            
            # Берем только FRAME элементы первого уровня
            if child_type == "FRAME":
                # Извлекаем данные фрейма (С ПОЛНОЙ ВЛОЖЕННОСТЬЮ)
                frame_data = self._extract_frame_data(child, child_id, design_tokens)
                frame_data["parent"] = "root"
                
                # Сохраняем фрейм в отдельный файл
                self._save_single_frame(frame_data)
                
                total_elements = self._count_total_elements(child)
                
                frames_data["parent_frames"].append({
                    "id": child_id,
                    "name": child_name,
                    "element_count": len(child.get("children", [])),
                    "total_elements": total_elements,  # Включая вложенные
                    "file": f"frames/{child_id}_{self._sanitize_name(child_name)}.json"
                })
                
                frames_data["frame_map"][child_id] = frame_data
                self.frames_count += 1
                
                print(f"   📦 Родительский фрейм '{child_name}' -> {total_elements} элементов (включая вложенные)")
    
    def _extract_frame_data(self, frame_element: Dict[str, Any], frame_id: str, design_tokens: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекаем данные для отдельного фрейма с ПОЛНОЙ ВЛОЖЕННОСТЬЮ"""
        return {
            "id": frame_id,
            "name": frame_element.get("name", ""),
            "type": frame_element.get("type", ""),
            "size": frame_element.get("size", {}),
            "position": frame_element.get("position", {}),
            "styles": frame_element.get("styles", {}),
            "layout": frame_element.get("layout", {}),
            "children": frame_element.get("children", []),  # СОХРАНЯЕМ ПОЛНУЮ ВЛОЖЕННОСТЬ
            "element_count": len(frame_element.get("children", [])),
            "total_elements": self._count_total_elements(frame_element),  # Всего элементов включая вложенные
            "design_tokens": self._extract_frame_design_tokens(frame_element),
            "global_design_tokens": {
                "colors": dict(list(design_tokens.get("colors", {}).items())[:10]),
                "typography": dict(list(design_tokens.get("typography", {}).items())[:5]),
                "spacing": dict(list(design_tokens.get("spacing", {}).items())[:5]),
                "border_radius": dict(list(design_tokens.get("border_radius", {}).items())[:5])
            }
        }
    
    def _count_total_elements(self, element: Dict[str, Any]) -> int:
        """Считаем общее количество элементов включая всех детей"""
        count = 1  # Сам элемент
        
        for child in element.get("children", []):
            count += self._count_total_elements(child)
        
        return count
    
    def _extract_frame_design_tokens(self, frame_element: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекаем дизайн-токены, используемые в этом фрейме"""
        colors = set()
        typography_styles = []
        spacing_values = set()
        radius_values = set()
        
        def collect_tokens(element: Dict[str, Any]):
            # Собираем цвета
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
            if typo and any(typo.values()):
                typography_styles.append(typo)
            
            # Собираем spacing
            layout = element.get("layout", {})
            spacing = layout.get("spacing", 0)
            if spacing > 0:
                spacing_values.add(spacing)
            
            padding = layout.get("padding", {})
            for key in ["left", "right", "top", "bottom"]:
                padding_val = padding.get(key, 0)
                if padding_val > 0:
                    spacing_values.add(padding_val)
            
            # Собираем border radius
            border_radius = element.get("styles", {}).get("border", {}).get("radius", 0)
            if border_radius > 0:
                radius_values.add(border_radius)
            
            # Рекурсивно для детей
            for child in element.get("children", []):
                collect_tokens(child)
        
        collect_tokens(frame_element)
        
        return {
            "colors": list(colors),
            "typography": typography_styles,
            "spacing": sorted(list(spacing_values)),
            "border_radius": sorted(list(radius_values))
        }
    
    def _save_single_frame(self, frame_data: Dict[str, Any]):
        """Сохраняем отдельный фрейм в JSON файл"""
        filename = f"{frame_data['id']}_{self._sanitize_name(frame_data['name'])}.json"
        filepath = os.path.join(self.frames_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _save_frames_metadata(self, frames_data: Dict[str, Any]):
        """Сохраняем мета-информацию о всех фреймах"""
        metadata = {
            "root_frame": {
                "name": frames_data["root_frame"]["name"],
                "element_count": frames_data["root_frame"]["element_count"],
                "total_elements": frames_data["root_frame"]["total_elements"],
                "file": "root_frame.json"
            },
            "parent_frames": frames_data["parent_frames"],
            "total_frames": frames_data["total_frames"]
        }
        
        # Сохраняем корневой фрейм
        root_filepath = os.path.join(self.frames_dir, "root_frame.json")
        with open(root_filepath, "w", encoding="utf-8") as f:
            json.dump(frames_data["root_frame"], f, indent=2, ensure_ascii=False, default=str)
        
        # Сохраняем метаданные
        meta_filepath = os.path.join(self.output_dir, "frames_metadata.json")
        with open(meta_filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        # Создаем индекс для навигации
        self._create_frames_index(metadata)
    
    def _create_frames_index(self, metadata: Dict[str, Any]):
        """Создаем индекс для навигации по фреймам"""
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
        
        index_filepath = os.path.join(self.frames_dir, "FRAMES_INDEX.md")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
    
    def _format_parent_frames_list(self, frames: List[Dict[str, Any]]) -> str:
        """Форматируем список родительских фреймов"""
        lines = []
        for frame in frames:
            lines.append(f"- **{frame['name']}**")
            lines.append(f"  - ID: `{frame['id']}`")
            lines.append(f"  - Элементов: {frame['element_count']}")
            lines.append(f"  - Всего с вложенными: {frame['total_elements']}")
            lines.append(f"  - Файл: `{frame['file']}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def _sanitize_name(self, name: str) -> str:
        """Очистка имени для файла"""
        return "".join(c if c.isalnum() else "_" for c in name.lower())[:30]