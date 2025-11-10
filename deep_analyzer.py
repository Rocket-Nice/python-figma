# deep_analyzer.py
import json
from typing import Dict, Any, List, Set
from config import Config

class DeepFigmaAnalyzer:
    def __init__(self):
        self.analysis_result = {
            "target_node": {},
            "full_hierarchy": [],
            "all_elements": [],
            "design_tokens": {
                "colors": set(),
                "typography": [],
                "spacing": set(),
                "border_radius": set()
            },
            "layout_data": {},
            "statistics": {}
        }
        self.element_counter = 0
    
    def analyze_completely(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Полный рекурсивный анализ всей структуры ноды"""
        print("🔍 Запускаем ПОЛНЫЙ анализ структуры Figma...")
        
        # Получаем целевую ноду
        specific_node_data = figma_data["specific_node"]["nodes"].get(Config.FIGMA_NODE_ID, {})
        if not specific_node_data:
            return self.analysis_result
        
        target_document = specific_node_data.get("document", {})
        
        # Анализируем целевую ноду как корень
        print(f"🎯 Анализируем корневую ноду: {target_document.get('name', 'Unknown')}")
        root_analysis = self._analyze_element_completely(target_document, "root", 0)
        self.analysis_result["target_node"] = root_analysis
        self.analysis_result["full_hierarchy"] = root_analysis.get("children", [])
        
        # Собираем все элементы в плоский список
        self._flatten_hierarchy(root_analysis)
        
        # Создаем финальные дизайн-токены
        self._create_final_design_tokens()
        
        # Собираем статистику
        self._collect_statistics()
        
        print(f"✅ Полный анализ завершен! Элементов: {self.analysis_result['statistics']['total_elements']}")
        return self.analysis_result
    
    def _analyze_element_completely(self, node: Dict[str, Any], element_id: str, depth: int) -> Dict[str, Any]:
        """Рекурсивный анализ элемента со ВСЕМИ деталями и полной вложенностью"""
        self.element_counter += 1
        element_number = self.element_counter
        
        if depth > 20:  # Защита от бесконечной рекурсии
            return {"error": "max_depth_exceeded"}
        
        # Базовые свойства
        bounding_box = node.get("absoluteBoundingBox", {})
        styles = self._extract_complete_styles(node)
        
        element_data = {
            "id": f"{element_id}-{element_number}",
            "original_id": node.get("id", ""),
            "name": node.get("name", ""),
            "type": node.get("type", ""),
            "depth": depth,
            "size": {
                "width": bounding_box.get("width", 0),
                "height": bounding_box.get("height", 0)
            },
            "position": {
                "x": bounding_box.get("x", 0),
                "y": bounding_box.get("y", 0)
            },
            "layout": {
                "mode": node.get("layoutMode", "NONE"),
                "spacing": node.get("itemSpacing", 0),
                "padding": {
                    "left": node.get("paddingLeft", 0),
                    "right": node.get("paddingRight", 0),
                    "top": node.get("paddingTop", 0),
                    "bottom": node.get("paddingBottom", 0)
                },
                "constraints": node.get("constraints", {})
            },
            "styles": styles,
            "content": self._extract_complete_content(node),
            "effects": self._extract_effects(node),
            "visibility": node.get("visible", True),
            "locked": node.get("locked", False),
            "children": []
        }
        
        # Логируем анализ (только первые 3 уровня для читаемости)
        if depth <= 3:
            indent = "  " * depth
            print(f"{indent}📦 {element_data['name']} ({element_data['type']}) - {element_data['size']['width']}×{element_data['size']['height']}")
        
        # Рекурсивный анализ детей (СОХРАНЯЕМ ПОЛНУЮ ВЛОЖЕННОСТЬ)
        children = node.get("children", [])
        for i, child in enumerate(children):
            child_analysis = self._analyze_element_completely(child, f"{element_id}-{element_number}", depth + 1)
            element_data["children"].append(child_analysis)
        
        return element_data
    
    def _extract_complete_styles(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Полное извлечение всех стилей элемента"""
        fills = node.get("fills", [])
        strokes = node.get("strokes", [])
        
        background_color = self._extract_color(fills)
        border_color = self._extract_color(strokes)
        border_radius = node.get("cornerRadius", 0)
        
        # Сохраняем в дизайн-токены
        if background_color:
            self.analysis_result["design_tokens"]["colors"].add(background_color)
        if border_color:
            self.analysis_result["design_tokens"]["colors"].add(border_color)
        if border_radius > 0:
            self.analysis_result["design_tokens"]["border_radius"].add(border_radius)
        
        # Сохраняем отступы
        spacing = node.get("itemSpacing", 0)
        if spacing > 0:
            self.analysis_result["design_tokens"]["spacing"].add(spacing)
        
        return {
            "background": background_color,
            "border": {
                "color": border_color,
                "width": self._extract_border_width(strokes),
                "radius": border_radius
            },
            "opacity": node.get("opacity", 1),
            "blend_mode": node.get("blendMode", "PASS_THROUGH"),
            "typography": self._extract_complete_typography(node),
            "fills": self._extract_fills_details(fills),
            "strokes": self._extract_strokes_details(strokes)
        }
    
    def _extract_complete_typography(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Полное извлечение типографики"""
        if node.get("type") != "TEXT":
            return {}
        
        style = node.get("style", {})
        fills = node.get("fills", [])
        color = self._extract_color(fills)
        
        typo_data = {
            "font_family": style.get("fontFamily", "Inter"),
            "font_size": style.get("fontSize", 16),
            "font_weight": style.get("fontWeight", 400),
            "line_height": style.get("lineHeight", {}),
            "letter_spacing": style.get("letterSpacing", {}),
            "text_align": style.get("textAlign", "LEFT"),
            "text_case": style.get("textCase", "ORIGINAL"),
            "text_decoration": style.get("textDecoration", "NONE"),
            "color": color,
            "paragraph_spacing": style.get("paragraphSpacing", 0)
        }
        
        # Сохраняем в дизайн-токены
        if any(typo_data.values()):
            self.analysis_result["design_tokens"]["typography"].append(typo_data)
        
        return typo_data
    
    def _extract_complete_content(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Полное извлечение контента"""
        content = {
            "type": node.get("type", "").lower(),
            "text": node.get("characters", "") if node.get("type") == "TEXT" else "",
            "name": node.get("name", ""),
            "description": node.get("description", "")
        }
        
        # Для изображений и векторных элементов
        if node.get("type") in ["RECTANGLE", "ELLIPSE", "VECTOR", "LINE"]:
            content["shape_type"] = node.get("type")
            fills = node.get("fills", [])
            if fills:
                content["fill_type"] = fills[0].get("type", "SOLID")
        
        return content
    
    def _extract_effects(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлечение эффектов (тени и т.д.)"""
        effects = node.get("effects", [])
        effect_data = []
        
        for effect in effects:
            effect_data.append({
                "type": effect.get("type", ""),
                "radius": effect.get("radius", 0),
                "color": self._extract_color([effect]) if effect.get("color") else None,
                "offset": effect.get("offset", {}),
                "spread": effect.get("spread", 0)
            })
        
        return effect_data
    
    def _extract_fills_details(self, fills: List[Dict]) -> List[Dict[str, Any]]:
        """Детальная информация о заливках"""
        fills_data = []
        for fill in fills:
            fills_data.append({
                "type": fill.get("type", "SOLID"),
                "color": self._extract_color([fill]),
                "opacity": fill.get("opacity", 1),
                "blend_mode": fill.get("blendMode", "NORMAL")
            })
        return fills_data
    
    def _extract_strokes_details(self, strokes: List[Dict]) -> List[Dict[str, Any]]:
        """Детальная информация об обводках"""
        strokes_data = []
        for stroke in strokes:
            strokes_data.append({
                "type": stroke.get("type", "SOLID"),
                "color": self._extract_color([stroke]),
                "weight": stroke.get("strokeWeight", 1),
                "align": stroke.get("strokeAlign", "INSIDE")
            })
        return strokes_data
    
    def _extract_color(self, fills: List[Dict]) -> str:
        """Извлечение цвета"""
        if not fills or fills[0].get("type") != "SOLID":
            return None
        
        color_data = fills[0].get("color", {})
        r = int(color_data.get("r", 0) * 255)
        g = int(color_data.get("g", 0) * 255)
        b = int(color_data.get("b", 0) * 255)
        a = color_data.get("a", 1)
        
        if a < 1.0:
            return f"rgba({r}, {g}, {b}, {round(a, 2)})"
        else:
            return f"#{r:02x}{g:02x}{b:02x}"
    
    def _extract_border_width(self, strokes: List[Dict]) -> float:
        """Извлечение ширины границы"""
        if not strokes:
            return 0
        return strokes[0].get("strokeWeight", 1)
    
    def _flatten_hierarchy(self, element: Dict[str, Any]):
        """Преобразование иерархии в плоский список всех элементов"""
        # Добавляем текущий элемент (без детей)
        element_flat = element.copy()
        element_flat.pop("children", None)
        self.analysis_result["all_elements"].append(element_flat)
        
        # Рекурсивно добавляем детей
        for child in element.get("children", []):
            self._flatten_hierarchy(child)
    
    def _create_final_design_tokens(self):
        """Создание финальной структуры дизайн-токенов"""
        # Преобразуем set в list и сортируем
        colors_list = sorted(list(self.analysis_result["design_tokens"]["colors"]))
        spacing_list = sorted(list(self.analysis_result["design_tokens"]["spacing"]))
        radius_list = sorted(list(self.analysis_result["design_tokens"]["border_radius"]))
        
        # Создаем именованные токены
        colors_dict = {}
        for i, color in enumerate(colors_list):
            if i == 0:
                colors_dict["primary"] = color
            elif i == 1:
                colors_dict["secondary"] = color
            elif i == 2:
                colors_dict["accent"] = color
            else:
                colors_dict[f"gray-{i-2}"] = color
        
        spacing_dict = {}
        for i, spacing in enumerate(spacing_list):
            spacing_names = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
            name = spacing_names[i] if i < len(spacing_names) else f"spacing-{i+1}"
            spacing_dict[name] = f"{spacing}px"
        
        radius_dict = {}
        for i, radius in enumerate(radius_list):
            radius_names = ["sm", "md", "lg", "xl", "2xl"]
            name = radius_names[i] if i < len(radius_names) else f"radius-{i+1}"
            radius_dict[name] = f"{radius}px"
        
        # Группируем типографику
        typography_dict = {}
        for typo in self.analysis_result["design_tokens"]["typography"]:
            size = typo.get("font_size", 16)
            weight = typo.get("font_weight", 400)
            
            if size >= 32:
                key = "heading-1"
            elif size >= 24:
                key = "heading-2"
            elif size >= 20:
                key = "heading-3"
            elif size >= 18:
                key = "heading-4"
            elif weight >= 600:
                key = "bold"
            else:
                key = "body"
            
            typography_dict[key] = typo
        
        self.analysis_result["design_tokens"] = {
            "colors": colors_dict,
            "typography": typography_dict,
            "spacing": spacing_dict,
            "border_radius": radius_dict
        }
    
    def _collect_statistics(self):
        """Сбор статистики по анализу"""
        elements = self.analysis_result["all_elements"]
        
        # Считаем по типам
        type_counts = {}
        for element in elements:
            elem_type = element.get("type", "unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        self.analysis_result["statistics"] = {
            "total_elements": len(elements),
            "type_counts": type_counts,
            "total_colors": len(self.analysis_result["design_tokens"]["colors"]),
            "total_typography_styles": len(self.analysis_result["design_tokens"]["typography"]),
            "max_depth": max([elem.get("depth", 0) for elem in elements]) if elements else 0
        }