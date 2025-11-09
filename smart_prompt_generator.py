# smart_prompt_generator.py
import json
import os
from typing import Dict, Any, List
from config import Config

class SmartPromptGenerator:
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.prompts_dir = os.path.join(self.output_dir, "smart_prompts")
        os.makedirs(self.prompts_dir, exist_ok=True)
    
    def generate_smart_prompts(self, analysis: Dict[str, Any]):
        """Генерация умных промптов с разделением по логическим частям"""
        print("🧠 Генерируем умные промпты с разделением...")
        
        # Сохраняем полный анализ
        self._save_full_analysis(analysis)
        
        # 1. Основной промпт с общей структурой
        self._generate_main_structure_prompt(analysis)
        
        # 2. Промпты для каждого уровня вложенности (первые 3 уровня)
        self._generate_level_prompts(analysis)
        
        # 3. Промпты по типам элементов
        self._generate_type_based_prompts(analysis)
        
        # 4. Промпты для дизайн-системы
        self._generate_design_system_prompts(analysis)
        
        # 5. Промпты для сложных компонентов
        self._generate_component_prompts(analysis)
        
        # Создаем инструкцию
        self._create_smart_instructions(analysis)
        
        print(f"✅ Умные промпты сохранены в: {self.prompts_dir}")
    
    def _save_full_analysis(self, analysis: Dict[str, Any]):
        """Сохранение полного анализа"""
        json_file = os.path.join(self.output_dir, "complete_analysis_full.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"📊 Полный анализ: {json_file}")
    
    def _generate_main_structure_prompt(self, analysis: Dict[str, Any]):
        """Основной промпт с общей структурой"""
        target = analysis["target_node"]
        stats = analysis["statistics"]
        
        prompt = f"""
# ОСНОВНАЯ СТРУКТУРА FIGMA МАКЕТА

## ОБЩАЯ ИНФОРМАЦИЯ:
- **Название**: {target.get('name', 'N/A')}
- **Размер**: {target.get('size', {}).get('width', 0)} × {target.get('size', {}).get('height', 0)} px
- **Всего элементов**: {stats['total_elements']}
- **Уровней вложенности**: {stats['max_depth']}
- **Основные типы элементов**: {', '.join(list(stats['type_counts'].keys())[:10])}

## КОРНЕВАЯ СТРУКТУРА (первые 2 уровня):
{self._format_root_structure(analysis['full_hierarchy'])}

## ДИЗАЙН-СИСТЕМА (основные токены):
{self._format_main_design_tokens(analysis['design_tokens'])}

## ОСНОВНЫЕ СЕКЦИИ МАКЕТА:
{self._identify_main_sections(analysis['full_hierarchy'])}

## ИНСТРУКЦИЯ ПО СБОРКЕ:
1. Начни с базовой HTML структуры на основе корневой иерархии
2. Используй промпты для каждого уровня вложенности из папки levels/
3. Для сложных компонентов используй промпты из папки components/
4. Следуй дизайн-системе из design_tokens.txt

## СЛЕДУЮЩИЙ ШАГ:
Используй промпты из папок levels/ и components/ для детальной реализации.
"""
        
        self._save_prompt("main_structure.txt", prompt)
    
    def _generate_level_prompts(self, analysis: Dict[str, Any]):
        """Промпты для каждого уровня вложенности"""
        levels_dir = os.path.join(self.prompts_dir, "levels")
        os.makedirs(levels_dir, exist_ok=True)
        
        # Анализируем первые 4 уровня (больше обычно не нужно)
        for level in range(4):
            level_elements = self._get_elements_by_level(analysis['all_elements'], level)
            if level_elements:
                prompt = self._create_level_prompt(level, level_elements, analysis['design_tokens'])
                self._save_prompt(f"levels/level_{level}.txt", prompt)
    
    def _generate_type_based_prompts(self, analysis: Dict[str, Any]):
        """Промпты по типам элементов"""
        types_dir = os.path.join(self.prompts_dir, "element_types")
        os.makedirs(types_dir, exist_ok=True)
        
        common_types = ['FRAME', 'TEXT', 'RECTANGLE', 'COMPONENT', 'INSTANCE', 'GROUP']
        
        for elem_type in common_types:
            type_elements = [e for e in analysis['all_elements'] if e.get('type') == elem_type]
            if type_elements:
                prompt = self._create_type_prompt(elem_type, type_elements[:20])  # Ограничиваем
                self._save_prompt(f"element_types/{elem_type.lower()}.txt", prompt)
    
    def _generate_design_system_prompts(self, analysis: Dict[str, Any]):
        """Промпты для дизайн-системы"""
        design_tokens = analysis['design_tokens']
        
        # Основные дизайн-токены
        tokens_prompt = f"""
# ДИЗАЙН-СИСТЕМА FIGMA МАКЕТА

## ЦВЕТОВАЯ ПАЛИТРА:
{self._format_colors_detailed(design_tokens['colors'])}

## ТИПОГРАФИЧЕСКАЯ СИСТЕМА:
{self._format_typography_detailed(design_tokens['typography'])}

## СИСТЕМА ОТСТУПОВ:
{self._format_spacing_detailed(design_tokens['spacing'])}

## RADIUS СИСТЕМА:
{self._format_radius_detailed(design_tokens['border_radius'])}

## КАК ИСПОЛЬЗОВАТЬ:
Создай CSS Custom Properties в :root с этими токенами.
Используй семантические имена переменных.
"""
        self._save_prompt("design_tokens.txt", tokens_prompt)
    
    def _generate_component_prompts(self, analysis: Dict[str, Any]):
        """Промпты для сложных компонентов"""
        components_dir = os.path.join(self.prompts_dir, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        # Находим сложные компоненты (фреймы с большим количеством детей)
        complex_frames = []
        for element in analysis['all_elements']:
            if element.get('type') == 'FRAME' and len(element.get('children', [])) > 5:
                complex_frames.append(element)
        
        # Берем топ-10 самых сложных компонентов
        complex_frames.sort(key=lambda x: len(x.get('children', [])), reverse=True)
        
        for i, component in enumerate(complex_frames[:10]):
            prompt = self._create_component_prompt(component, i+1)
            component_name = self._sanitize_name(component.get('name', f'component_{i+1}'))
            self._save_prompt(f"components/{component_name}.txt", prompt)
    
    def _format_root_structure(self, hierarchy: List[Dict[str, Any]]) -> str:
        """Форматирование корневой структуры"""
        lines = []
        
        def format_level(elements: List[Dict[str, Any]], depth: int = 0):
            for element in elements[:15]:  # Ограничиваем для читаемости
                indent = "  " * depth
                elem_type = element.get('type', 'UNKNOWN')
                elem_name = element.get('name', 'Unnamed')
                children_count = len(element.get('children', []))
                
                line = f"{indent}- **{elem_type}**: {elem_name}"
                if children_count > 0:
                    line += f" ({children_count} детей)"
                if element.get('styles', {}).get('background'):
                    line += f" | Фон: {element['styles']['background']}"
                
                lines.append(line)
                
                # Рекурсивно для детей (только 2 уровня)
                if depth < 2 and element.get('children'):
                    format_level(element['children'], depth + 1)
        
        format_level(hierarchy)
        return "\n".join(lines)
    
    def _format_main_design_tokens(self, design_tokens: Dict[str, Any]) -> str:
        """Форматирование основных дизайн-токенов"""
        lines = []
        
        # Цвета (первые 5)
        colors = list(design_tokens['colors'].items())[:5]
        if colors:
            lines.append("**Основные цвета:**")
            for name, color in colors:
                lines.append(f"- `{name}`: `{color}`")
        
        # Типографика (первые 3 стиля)
        typography = list(design_tokens['typography'].items())[:3]
        if typography:
            lines.append("\n**Основная типографика:**")
            for name, styles in typography:
                lines.append(f"- `{name}`: {styles.get('font_family')} {styles.get('font_size')}px")
        
        return "\n".join(lines)
    
    def _identify_main_sections(self, hierarchy: List[Dict[str, Any]]) -> str:
        """Идентификация основных секций макета"""
        sections = []
        
        for element in hierarchy[:10]:  # Первые 10 корневых детей
            if element.get('type') in ['FRAME', 'SECTION', 'GROUP']:
                elem_name = element.get('name', '').lower()
                section_type = self._classify_section(elem_name)
                sections.append(f"- **{element.get('name', 'Unnamed')}** ({section_type}) - {len(element.get('children', []))} элементов")
        
        return "\n".join(sections) if sections else "Не удалось идентифицировать секции"
    
    def _classify_section(self, name: str) -> str:
        """Классификация секций по имени"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['header', 'nav', 'menu']):
            return "Навигация"
        elif any(word in name_lower for word in ['hero', 'banner', 'main']):
            return "Hero секция"
        elif any(word in name_lower for word in ['footer', 'bottom']):
            return "Футер"
        elif any(word in name_lower for word in ['card', 'product', 'item']):
            return "Карточка"
        elif any(word in name_lower for word in ['button', 'btn', 'cta']):
            return "Кнопка"
        elif any(word in name_lower for word in ['form', 'input', 'field']):
            return "Форма"
        else:
            return "Секция"
    
    def _get_elements_by_level(self, all_elements: List[Dict[str, Any]], level: int) -> List[Dict[str, Any]]:
        """Получение элементов по уровню вложенности"""
        return [e for e in all_elements if e.get('depth', 0) == level][:50]  # Ограничиваем
    
    def _create_level_prompt(self, level: int, elements: List[Dict[str, Any]], design_tokens: Dict[str, Any]) -> str:
        """Создание промпта для уровня вложенности"""
        return f"""
# УРОВЕНЬ {level}: ДЕТАЛЬНАЯ СТРУКТУРА

## ЭЛЕМЕНТЫ НА УРОВНЕ {level}:
{self._format_level_elements(elements)}

## ОСОБЕННОСТИ УРОВНЯ {level}:
{self._analyze_level_patterns(elements)}

## ДИЗАЙН-ТОКЕНЫ ДЛЯ ЭТОГО УРОВНЯ:
{self._extract_level_tokens(elements, design_tokens)}

## ЗАДАЧА:
Создай HTML и CSS для элементов этого уровня.
Учти их взаимное расположение и стили.
"""
    
    def _create_type_prompt(self, elem_type: str, elements: List[Dict[str, Any]]) -> str:
        """Создание промпта для типа элементов"""
        return f"""
# ТИП ЭЛЕМЕНТА: {elem_type}

## ОБРАЗЦЫ ЭЛЕМЕНТОВ ({len(elements)} шт):
{self._format_type_examples(elements)}

## ОБЩИЕ СВОЙСТВА:
{self._analyze_type_patterns(elements)}

## РЕКОМЕНДАЦИИ ПО РЕАЛИЗАЦИИ:
{self._get_type_implementation_guide(elem_type)}

## ЗАДАЧА:
Создай универсальные стили и компоненты для элементов типа {elem_type}.
"""
    
    def _create_component_prompt(self, component: Dict[str, Any], index: int) -> str:
        """Создание промпта для сложного компонента"""
        return f"""
# СЛОЖНЫЙ КОМПОНЕНТ {index}: {component.get('name', 'Unnamed')}

## ОСНОВНЫЕ ХАРАКТЕРИСТИКИ:
- Тип: {component.get('type')}
- Размер: {component.get('size', {}).get('width')} × {component.get('size', {}).get('height')} px
- Дочерних элементов: {len(component.get('children', []))}
- Фон: {component.get('styles', {}).get('background', 'прозрачный')}

## СТРУКТУРА КОМПОНЕНТА:
{self._format_component_structure(component)}

## СТИЛИ КОМПОНЕНТА:
{self._format_component_styles(component)}

## ЗАДАЧА:
Создай самостоятельный компонент с этой структурой и стилями.
Компонент должен быть переиспользуемым.
"""
    
    def _format_level_elements(self, elements: List[Dict[str, Any]]) -> str:
        """Форматирование элементов уровня"""
        lines = []
        for elem in elements[:25]:  # Ограничиваем
            line = f"- **{elem.get('type')}**: {elem.get('name')}"
            line += f" | {elem.get('size', {}).get('width')}×{elem.get('size', {}).get('height')}px"
            if elem.get('styles', {}).get('background'):
                line += f" | Фон: {elem['styles']['background']}"
            lines.append(line)
        return "\n".join(lines)
    
    def _format_component_structure(self, component: Dict[str, Any]) -> str:
        """Форматирование структуры компонента"""
        lines = []
        
        def format_children(children: List[Dict[str, Any]], depth: int = 1):
            for child in children[:10]:  # Ограничиваем
                indent = "  " * depth
                line = f"{indent}- {child.get('type')}: {child.get('name')}"
                if child.get('styles', {}).get('background'):
                    line += f" | Фон: {child['styles']['background']}"
                lines.append(line)
                
                if depth < 3 and child.get('children'):
                    format_children(child['children'], depth + 1)
        
        if component.get('children'):
            format_children(component['children'])
        
        return "\n".join(lines) if lines else "Нет дочерних элементов"
    
    # Дополнительные методы форматирования...
    def _format_colors_detailed(self, colors: Dict[str, str]) -> str:
        return "\n".join([f"- `{name}`: `{color}`" for name, color in colors.items()])
    
    def _format_typography_detailed(self, typography: Dict[str, Any]) -> str:
        lines = []
        for name, styles in typography.items():
            lines.append(f"- `{name}`: {styles.get('font_family')} {styles.get('font_size')}px, вес {styles.get('font_weight')}")
        return "\n".join(lines)
    
    def _format_spacing_detailed(self, spacing: Dict[str, str]) -> str:
        return "\n".join([f"- `{name}`: `{value}`" for name, value in spacing.items()])
    
    def _format_radius_detailed(self, radius: Dict[str, str]) -> str:
        return "\n".join([f"- `{name}`: `{value}`" for name, value in radius.items()])
    
    def _analyze_level_patterns(self, elements: List[Dict[str, Any]]) -> str:
        """Анализ паттернов уровня"""
        if not elements:
            return "Нет элементов для анализа"
        
        # Простой анализ layout
        layout_modes = set(e.get('layout', {}).get('mode', 'NONE') for e in elements)
        avg_width = sum(e.get('size', {}).get('width', 0) for e in elements) / len(elements)
        
        patterns = []
        patterns.append(f"- Преобладающий layout: {', '.join(layout_modes)}")
        patterns.append(f"- Средняя ширина элементов: {avg_width:.1f}px")
        patterns.append(f"- Типы элементов: {', '.join(set(e.get('type', '') for e in elements))}")
        
        return "\n".join(patterns)
    
    def _analyze_type_patterns(self, elements: List[Dict[str, Any]]) -> str:
        """Анализ паттернов типа элементов"""
        if not elements:
            return "Нет элементов для анализа"
        
        props = []
        
        # Размеры
        widths = [e.get('size', {}).get('width', 0) for e in elements]
        heights = [e.get('size', {}).get('height', 0) for e in elements]
        
        props.append(f"- Количество: {len(elements)}")
        props.append(f"- Размеры: {min(widths)}-{max(widths)}px × {min(heights)}-{max(heights)}px")
        
        # Стили
        backgrounds = set(e.get('styles', {}).get('background') for e in elements if e.get('styles', {}).get('background'))
        if backgrounds:
            props.append(f"- Фоны: {', '.join(list(backgrounds)[:3])}")
        
        return "\n".join(props)
    
    def _get_type_implementation_guide(self, elem_type: str) -> str:
        """Рекомендации по реализации для типа элементов"""
        guides = {
            'FRAME': "Используй div с Flexbox/Grid. Учитывай padding и spacing.",
            'TEXT': "Используй семантические теги (h1-h6, p, span). Сохрани точные размеры шрифта.",
            'RECTANGLE': "Используй div с background-color. Учитывай border-radius.",
            'COMPONENT': "Создай переиспользуемый компонент с параметрами.",
            'INSTANCE': "Реализуй как экземпляр основного компонента.",
            'GROUP': "Используй div с относительным позиционированием."
        }
        return guides.get(elem_type, "Используй семантические HTML теги и современный CSS.")
    
    def _extract_level_tokens(self, elements: List[Dict[str, Any]], design_tokens: Dict[str, Any]) -> str:
        """Извлечение токенов для уровня"""
        tokens = []
        
        # Цвета используемые на этом уровне
        level_colors = set()
        for elem in elements:
            bg = elem.get('styles', {}).get('background')
            if bg:
                level_colors.add(bg)
        
        if level_colors:
            tokens.append("**Цвета уровня:**")
            for color in list(level_colors)[:5]:
                tokens.append(f"- `{color}`")
        
        return "\n".join(tokens) if tokens else "Стандартные токены дизайн-системы"
    
    def _format_type_examples(self, elements: List[Dict[str, Any]]) -> str:
        """Форматирование примеров элементов типа"""
        lines = []
        for elem in elements[:10]:  # Ограничиваем
            line = f"- **{elem.get('name')}**"
            line += f" | {elem.get('size', {}).get('width')}×{elem.get('size', {}).get('height')}px"
            if elem.get('styles', {}).get('background'):
                line += f" | Фон: {elem['styles']['background']}"
            lines.append(line)
        return "\n".join(lines)
    
    def _format_component_styles(self, component: Dict[str, Any]) -> str:
        """Форматирование стилей компонента"""
        styles = component.get('styles', {})
        lines = []
        
        if styles.get('background'):
            lines.append(f"- Фон: `{styles['background']}`")
        if styles.get('border', {}).get('color'):
            lines.append(f"- Граница: `{styles['border']['color']}`, {styles['border']['width']}px")
        if styles.get('border', {}).get('radius', 0) > 0:
            lines.append(f"- Border radius: {styles['border']['radius']}px")
        
        return "\n".join(lines) if lines else "Базовые стили"
    
    def _sanitize_name(self, name: str) -> str:
        """Очистка имени для файла"""
        return "".join(c if c.isalnum() else "_" for c in name.lower())[:30]
    
    def _save_prompt(self, filename: str, content: str):
        """Сохранение промпта в файл"""
        filepath = os.path.join(self.prompts_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _create_smart_instructions(self, analysis: Dict[str, Any]):
        """Создание инструкции для умных промптов"""
        stats = analysis["statistics"]
        
        instructions = f"""
# УМНЫЕ ПРОМПТЫ ДЛЯ FIGMA МАКЕТА

## ОБЩАЯ ИНФОРМАЦИЯ:
- Всего элементов: {stats['total_elements']}
- Уровней вложенности: {stats['max_depth']}
- Основных типов: {len(stats['type_counts'])}
- Сложных компонентов: {len([e for e in analysis['all_elements'] if e.get('type') == 'FRAME' and len(e.get('children', [])) > 5])}

## СТРУКТУРА ПРОМПТОВ:

### 📁 main_structure.txt - Основная структура
- Общая информация о макете
- Корневая иерархия (первые 2 уровня)
- Основные дизайн-токены
- Идентификация секций

### 📁 levels/ - Промпты по уровням вложенности
- level_0.txt - Корневые элементы
- level_1.txt - Элементы первого уровня
- level_2.txt - Элементы второго уровня
- level_3.txt - Элементы третьего уровня

### 📁 element_types/ - Промпты по типам элементов
- frame.txt - Фреймы и контейнеры
- text.txt - Текстовые элементы
- rectangle.txt - Прямоугольники и фигуры
- component.txt - Компоненты
- instance.txt - Инстансы

### 📁 components/ - Сложные компоненты
- Промпты для самых сложных компонентов макета
- Каждый файл - отдельный переиспользуемый компонент

### 📁 design_tokens.txt - Полная дизайн-система
- Цветовая палитра
- Типографическая система
- Система отступов
- Radius система

## ПОРЯДОК РАБОТЫ:
1. Начни с main_structure.txt для общей структуры
2. Используй levels/ для поэтапной реализации
3. Применяй element_types/ для стилизации конкретных типов
4. Реализуй сложные компоненты из components/
5. Следуй дизайн-системе из design_tokens.txt

## СОВЕТЫ:
- Работай с промптами последовательно
- Проверяй соответствие размеров и позиций
- Используй CSS Grid/Flexbox для сложных layout
- Создавай переиспользуемые компоненты
"""
        
        self._save_prompt("SMART_INSTRUCTIONS.md", instructions)