# deep_analyzer.py
import json
from typing import Dict, Any, List, Set
from config import Config

class DeepFigmaAnalyzer:
    """
    Глубокий анализатор Figma структур
    Рекурсивно анализирует всю иерархию элементов и извлекает дизайн-токены
    """
    
    def __init__(self):
        # Структура для хранения результатов анализа
        self.analysis_result = {
            "target_node": {},       # Детальный анализ целевой ноды
            "full_hierarchy": [],    # Полная иерархия в виде дерева
            "all_elements": [],      # Все элементы в плоском списке (для статистики)
            "design_tokens": {       # Извлеченные дизайн-токены (цвета, шрифты и т.д.)
                "colors": set(),     # Множество уникальных цветов
                "typography": [],    # Стили типографики
                "spacing": set(),    # Значения отступов
                "border_radius": set()  # Значения скруглений
            },
            "layout_data": {},       # Данные о компоновке
            "statistics": {}         # Статистика анализа
        }
        self.element_counter = 0  # Счетчик элементов для генерации ID
    
    def analyze_completely(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главный метод - запускает полный анализ Figma структуры
        figma_data: данные от FigmaClient.get_full_structure()
        """
        print("🔍 Запускаем ПОЛНЫЙ анализ структуры Figma...")
        
        # Извлекаем данные конкретной ноды из ответа Figma API
        specific_node_data = figma_data["specific_node"]["nodes"].get(Config.FIGMA_NODE_ID, {})
        if not specific_node_data:
            print("❌ Целевая нода не найдена в ответе Figma")
            return self.analysis_result
        
        # Получаем документ ноды (основные данные элемента)
        target_document = specific_node_data.get("document", {})
        
        # Запускаем рекурсивный анализ начиная с корневой ноды
        print(f"🎯 Анализируем корневую ноду: {target_document.get('name', 'Unknown')}")
        root_analysis = self._analyze_element_completely(target_document, "root", 0)
        
        # Сохраняем результаты
        self.analysis_result["target_node"] = root_analysis
        self.analysis_result["full_hierarchy"] = root_analysis.get("children", [])
        
        # Преобразуем иерархию в плоский список для удобства
        self._flatten_hierarchy(root_analysis)
        
        # Создаем финальные дизайн-токены (преобразуем множества в словари)
        self._create_final_design_tokens()
        
        # Собираем статистику
        self._collect_statistics()
        
        print(f"✅ Полный анализ завершен! Элементов: {self.analysis_result['statistics']['total_elements']}")
        return self.analysis_result
    
    def _analyze_element_completely(self, node: Dict[str, Any], element_id: str, depth: int) -> Dict[str, Any]:
        """
        Рекурсивно анализирует элемент и всех его детей
        node: данные элемента от Figma API
        element_id: уникальный ID для отслеживания
        depth: глубина вложенности (для отступов и защиты от бесконечной рекурсии)
        """
        # Защита от бесконечной рекурсии (максимум 20 уровней)
        if depth > 20:
            return {"error": "max_depth_exceeded"}
        
        # Увеличиваем счетчик и создаем номер элемента
        self.element_counter += 1
        element_number = self.element_counter
        
        # Получаем базовые геометрические данные
        bounding_box = node.get("absoluteBoundingBox", {})
        
        # Извлекаем все стили элемента
        styles = self._extract_complete_styles(node)
        
        # Создаем структуру данных для элемента
        element_data = {
            "id": f"{element_id}-{element_number}",  # Уникальный ID
            "original_id": node.get("id", ""),       # Оригинальный ID из Figma
            "name": node.get("name", ""),            # Имя элемента
            "type": node.get("type", ""),            # Тип (FRAME, TEXT, RECTANGLE и т.д.)
            "depth": depth,                          # Уровень вложенности
            "size": {                                # Размеры
                "width": bounding_box.get("width", 0),
                "height": bounding_box.get("height", 0)
            },
            "position": {                            # Позиция относительно родителя
                "x": bounding_box.get("x", 0),
                "y": bounding_box.get("y", 0)
            },
            "layout": {                              # Настройки лайаута
                "mode": node.get("layoutMode", "NONE"),  # FLEX, GRID и т.д.
                "spacing": node.get("itemSpacing", 0),   # Расстояние между элементами
                "padding": {                         # Внутренние отступы
                    "left": node.get("paddingLeft", 0),
                    "right": node.get("paddingRight", 0),
                    "top": node.get("paddingTop", 0),
                    "bottom": node.get("paddingBottom", 0)
                },
                "constraints": node.get("constraints", {})  # Ограничения позиционирования
            },
            "styles": styles,                        # Все стили элемента
            "content": self._extract_complete_content(node),  # Тексты и контент
            "effects": self._extract_effects(node),  # Тени, блюры и т.д.
            "visibility": node.get("visible", True), # Видимость элемента
            "locked": node.get("locked", False),     # Заблокирован ли элемент
            "children": []                           # Дочерние элементы
        }
        
        # Логируем анализ (только первые 3 уровня для читаемости)
        if depth <= 3:
            indent = "  " * depth  # Создаем отступы для дерева
            print(f"{indent}📦 {element_data['name']} ({element_data['type']}) - {element_data['size']['width']}×{element_data['size']['height']}")
        
        # РЕКУРСИВНЫЙ АНАЛИЗ ДЕТЕЙ - сохраняем полную вложенность!
        children = node.get("children", [])
        for i, child in enumerate(children):
            # Рекурсивно анализируем каждого ребенка
            child_analysis = self._analyze_element_completely(child, f"{element_id}-{element_number}", depth + 1)
            element_data["children"].append(child_analysis)
        
        return element_data
    
    def _extract_complete_styles(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает все стили элемента: цвета, границы, типографику и т.д.
        """
        # Получаем данные о заливках и обводках
        fills = node.get("fills", [])
        strokes = node.get("strokes", [])
        
        # Извлекаем основные стили
        background_color = self._extract_color(fills)
        border_color = self._extract_color(strokes)
        border_radius = node.get("cornerRadius", 0)
        
        # СОБИРАЕМ ДИЗАЙН-ТОКЕНЫ в общую копилку
        if background_color:
            self.analysis_result["design_tokens"]["colors"].add(background_color)
        if border_color:
            self.analysis_result["design_tokens"]["colors"].add(border_color)
        if border_radius > 0:
            self.analysis_result["design_tokens"]["border_radius"].add(border_radius)
        
        # Собираем значения отступов
        spacing = node.get("itemSpacing", 0)
        if spacing > 0:
            self.analysis_result["design_tokens"]["spacing"].add(spacing)
        
        # Возвращаем структурированные стили
        return {
            "background": background_color,
            "border": {
                "color": border_color,
                "width": self._extract_border_width(strokes),
                "radius": border_radius
            },
            "opacity": node.get("opacity", 1),      # Прозрачность (0-1)
            "blend_mode": node.get("blendMode", "PASS_THROUGH"),  # Режим смешивания
            "typography": self._extract_complete_typography(node),  # Шрифты и текст
            "fills": self._extract_fills_details(fills),    # Детали заливок
            "strokes": self._extract_strokes_details(strokes)  # Детали обводок
        }
    
    def _extract_complete_typography(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает все параметры типографики для текстовых элементов
        """
        # Работаем только с текстовыми элементами
        if node.get("type") != "TEXT":
            return {}
        
        # Получаем стили текста из Figma
        style = node.get("style", {})
        fills = node.get("fills", [])
        color = self._extract_color(fills)  # Цвет текста
        
        # Собираем все параметры шрифта
        typo_data = {
            "font_family": style.get("fontFamily", "Inter"),  # Семейство шрифта
            "font_size": style.get("fontSize", 16),           # Размер шрифта
            "font_weight": style.get("fontWeight", 400),      # Жирность (400=normal, 700=bold)
            "line_height": style.get("lineHeight", {}),       # Межстрочный интервал
            "letter_spacing": style.get("letterSpacing", {}), # Межбуквенный интервал
            "text_align": style.get("textAlign", "LEFT"),     # Выравнивание
            "text_case": style.get("textCase", "ORIGINAL"),   # Регистр (UPPERCASE и т.д.)
            "text_decoration": style.get("textDecoration", "NONE"),  # Подчеркивание
            "color": color,                                   # Цвет текста
            "paragraph_spacing": style.get("paragraphSpacing", 0)   # Отступ между параграфами
        }
        
        # Сохраняем в дизайн-токены если есть какие-то данные
        if any(typo_data.values()):
            self.analysis_result["design_tokens"]["typography"].append(typo_data)
        
        return typo_data
    
    def _extract_complete_content(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает контент элемента: тексты, описания и т.д.
        """
        content = {
            "type": node.get("type", "").lower(),    # Тип элемента в нижнем регистре
            "text": node.get("characters", "") if node.get("type") == "TEXT" else "",  # Текст для текстовых элементов
            "name": node.get("name", ""),            # Имя элемента
            "description": node.get("description", "")  # Описание (если есть)
        }
        
        # Для графических элементов добавляем информацию о форме
        if node.get("type") in ["RECTANGLE", "ELLIPSE", "VECTOR", "LINE"]:
            content["shape_type"] = node.get("type")  # Тип фигуры
            fills = node.get("fills", [])
            if fills:
                content["fill_type"] = fills[0].get("type", "SOLID")  # Тип заливки
        
        return content
    
    def _extract_effects(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Извлекает эффекты: тени, размытия и т.д.
        """
        effects = node.get("effects", [])
        effect_data = []
        
        for effect in effects:
            effect_data.append({
                "type": effect.get("type", ""),      # Тип эффекта (DROP_SHADOW и т.д.)
                "radius": effect.get("radius", 0),   # Радиус размытия
                "color": self._extract_color([effect]) if effect.get("color") else None,  # Цвет эффекта
                "offset": effect.get("offset", {}),  # Смещение тени
                "spread": effect.get("spread", 0)    # Распространение тени
            })
        
        return effect_data
    
    def _extract_fills_details(self, fills: List[Dict]) -> List[Dict[str, Any]]:
        """
        Детальная информация о заливках элемента
        """
        fills_data = []
        for fill in fills:
            fills_data.append({
                "type": fill.get("type", "SOLID"),    # Тип заливки (SOLID, GRADIENT, IMAGE)
                "color": self._extract_color([fill]), # Цвет заливки
                "opacity": fill.get("opacity", 1),    # Прозрачность заливки
                "blend_mode": fill.get("blendMode", "NORMAL")  # Режим смешивания
            })
        return fills_data
    
    def _extract_strokes_details(self, strokes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Детальная информация об обводках (границах)
        """
        strokes_data = []
        for stroke in strokes:
            strokes_data.append({
                "type": stroke.get("type", "SOLID"),     # Тип обводки
                "color": self._extract_color([stroke]),  # Цвет обводки
                "weight": stroke.get("strokeWeight", 1), # Толщина обводки
                "align": stroke.get("strokeAlign", "INSIDE")  # Выравнивание обводки
            })
        return strokes_data
    
    def _extract_color(self, fills: List[Dict]) -> str:
        """
        Извлекает цвет из заливок и преобразует в CSS-формат
        Возвращает строку в формате #RRGGBB или rgba(r, g, b, a)
        """
        # Проверяем что есть заливки и они solid (не градиент)
        if not fills or fills[0].get("type") != "SOLID":
            return None
        
        # Получаем данные цвета из Figma (значения от 0 до 1)
        color_data = fills[0].get("color", {})
        r = int(color_data.get("r", 0) * 255)  # Красный (0-255)
        g = int(color_data.get("g", 0) * 255)  # Зеленый (0-255)
        b = int(color_data.get("b", 0) * 255)  # Синий (0-255)
        a = color_data.get("a", 1)             # Альфа-канал (прозрачность 0-1)
        
        # Форматируем в CSS в зависимости от прозрачности
        if a < 1.0:
            # Для полупрозрачных цветов используем rgba
            return f"rgba({r}, {g}, {b}, {round(a, 2)})"
        else:
            # Для непрозрачных - hex формат
            return f"#{r:02x}{g:02x}{b:02x}"
    
    def _extract_border_width(self, strokes: List[Dict]) -> float:
        """
        Извлекает ширину границы (обводки)
        """
        if not strokes:
            return 0
        return strokes[0].get("strokeWeight", 1)  # Толщина обводки в пикселях
    
    def _flatten_hierarchy(self, element: Dict[str, Any]):
        """
        Преобразует древовидную структуру в плоский список
        Нужно для статистики и быстрого поиска элементов
        """
        # Создаем копию элемента без детей и добавляем в плоский список
        element_flat = element.copy()
        element_flat.pop("children", None)  # Удаляем детей из копии
        self.analysis_result["all_elements"].append(element_flat)
        
        # Рекурсивно обрабатываем всех детей
        for child in element.get("children", []):
            self._flatten_hierarchy(child)
    
    def _create_final_design_tokens(self):
        """
        Преобразует сырые токены (множества) в именованные словари
        Создает удобную структуру для использования в коде
        """
        # Преобразуем множества в отсортированные списки
        colors_list = sorted(list(self.analysis_result["design_tokens"]["colors"]))
        spacing_list = sorted(list(self.analysis_result["design_tokens"]["spacing"]))
        radius_list = sorted(list(self.analysis_result["design_tokens"]["border_radius"]))
        
        # СОЗДАЕМ ИМЕНОВАННЫЕ ТОКЕНЫ ЦВЕТОВ
        colors_dict = {}
        for i, color in enumerate(colors_list):
            if i == 0:
                colors_dict["primary"] = color      # Первый цвет = основной
            elif i == 1:
                colors_dict["secondary"] = color    # Второй цвет = второстепенный
            elif i == 2:
                colors_dict["accent"] = color       # Третий цвет = акцентный
            else:
                colors_dict[f"gray-{i-2}"] = color  # Остальные = оттенки серого
        
        # СОЗДАЕМ ИМЕНОВАННЫЕ ТОКЕНЫ ОТСТУПОВ
        spacing_dict = {}
        for i, spacing in enumerate(spacing_list):
            spacing_names = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]  # Стандартные имена
            name = spacing_names[i] if i < len(spacing_names) else f"spacing-{i+1}"
            spacing_dict[name] = f"{spacing}px"  # Сохраняем с единицами измерения
        
        # СОЗДАЕМ ИМЕНОВАННЫЕ ТОКЕНЫ СКРУГЛЕНИЙ
        radius_dict = {}
        for i, radius in enumerate(radius_list):
            radius_names = ["sm", "md", "lg", "xl", "2xl"]
            name = radius_names[i] if i < len(radius_names) else f"radius-{i+1}"
            radius_dict[name] = f"{radius}px"
        
        # ГРУППИРУЕМ ТИПОГРАФИКУ ПО РАЗМЕРАМ И ВЕСУ
        typography_dict = {}
        for typo in self.analysis_result["design_tokens"]["typography"]:
            size = typo.get("font_size", 16)
            weight = typo.get("font_weight", 400)
            
            # Классифицируем стили по размерам
            if size >= 32:
                key = "heading-1"      # Заголовок 1 уровня
            elif size >= 24:
                key = "heading-2"      # Заголовок 2 уровня
            elif size >= 20:
                key = "heading-3"      # Заголовок 3 уровня
            elif size >= 18:
                key = "heading-4"      # Заголовок 4 уровня
            elif weight >= 600:
                key = "bold"           # Жирный текст
            else:
                key = "body"           # Основной текст
            
            typography_dict[key] = typo
        
        # ЗАМЕНЯЕМ СЫРЫЕ ДАННЫЕ НА СТРУКТУРИРОВАННЫЕ ТОКЕНЫ
        self.analysis_result["design_tokens"] = {
            "colors": colors_dict,
            "typography": typography_dict,
            "spacing": spacing_dict,
            "border_radius": radius_dict
        }
    
    def _collect_statistics(self):
        """
        Собирает статистику по анализу: количество элементов, типы и т.д.
        """
        elements = self.analysis_result["all_elements"]
        
        # СЧИТАЕМ ЭЛЕМЕНТЫ ПО ТИПАМ
        type_counts = {}
        for element in elements:
            elem_type = element.get("type", "unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        # СОХРАНЯЕМ СТАТИСТИКУ
        self.analysis_result["statistics"] = {
            "total_elements": len(elements),  # Общее количество элементов
            "type_counts": type_counts,       # Количество по типам
            "total_colors": len(self.analysis_result["design_tokens"]["colors"]),
            "total_typography_styles": len(self.analysis_result["design_tokens"]["typography"]),
            "max_depth": max([elem.get("depth", 0) for elem in elements]) if elements else 0  # Максимальная вложенность
        }