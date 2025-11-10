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
    
    def generate_smart_prompts(self, analysis: Dict[str, Any], frames_data: Dict[str, Any] = None):
        """Генерация умных промптов для родительских фреймов первого уровня"""
        print("🧠 Генерируем умные промпты для родительских фреймов...")
        
        # Сохраняем полный анализ
        self._save_full_analysis(analysis)
        
        if frames_data:
            # Генерируем промпты для каждого родительского фрейма
            self._generate_parent_frames_prompts(frames_data)
        else:
            # Старая логика (для обратной совместимости)
            self._generate_legacy_prompts(analysis)
        
        # Создаем инструкцию
        self._create_smart_instructions(analysis, frames_data)
        
        print(f"✅ Умные промпты сохранены в: {self.prompts_dir}")
    
    def _generate_parent_frames_prompts(self, frames_data: Dict[str, Any]):
        """Генерация промптов на основе родительских фреймов первого уровня"""
        frames_prompts_dir = os.path.join(self.prompts_dir, "parent_frames")
        os.makedirs(frames_prompts_dir, exist_ok=True)
        
        # Промпт для корневого фрейма
        self._generate_root_frame_prompt(frames_data["root_frame"])
        
        # Промпты для родительских фреймов первого уровня
        for frame_info in frames_data["parent_frames"]:
            frame_file = os.path.join(self.output_dir, frame_info["file"])
            if os.path.exists(frame_file):
                with open(frame_file, "r", encoding="utf-8") as f:
                    frame_data = json.load(f)
                self._generate_parent_frame_prompt(frame_data, frame_info)
    
    def _generate_root_frame_prompt(self, root_frame: Dict[str, Any]):
        """Генерация промпта для корневого фрейма"""
        prompt = f"""
# КОРНЕВОЙ ФРЕЙМ: {root_frame.get('name', 'N/A')}

## ОСНОВНЫЕ ХАРАКТЕРИСТИКИ:
- **Тип**: {root_frame.get('type', 'N/A')}
- **Размер**: {root_frame.get('size', {}).get('width', 0)} × {root_frame.get('size', {}).get('height', 0)} px
- **Непосредственных детей**: {root_frame.get('element_count', 0)}
- **Всего элементов (с вложенными)**: {root_frame.get('total_elements', 0)}
- **Положение**: X: {root_frame.get('position', {}).get('x', 0)}, Y: {root_frame.get('position', {}).get('y', 0)}

## СТИЛИ КОРНЕВОГО ФРЕЙМА:
{self._format_frame_styles(root_frame.get('styles', {}))}

## ЛАЙАУТ НАСТРОЙКИ:
{self._format_frame_layout(root_frame.get('layout', {}))}

## РОДИТЕЛЬСКИЕ ФРЕЙМЫ ПЕРВОГО УРОВНЯ:
{self._format_parent_frames_overview(root_frame.get('children', []))}

## ДИЗАЙН-ТОКЕНЫ:
{self._format_frame_design_tokens(root_frame.get('design_tokens', {}))}

## ГЛОБАЛЬНЫЕ ТОКЕНЫ:
{self._format_global_tokens(root_frame.get('global_design_tokens', {}))}

## ЗАДАЧА:
Создай основную HTML структуру и базовые стили для этого корневого фрейма.
Это контейнер для всех родительских фреймов первого уровня.
Подготовь структуру для размещения следующих секций:
{self._list_parent_frames_names(root_frame.get('children', []))}

## ВАЖНО:
Этот фрейм является контейнером для всего макета.
Родительские фреймы первого уровня будут реализованы отдельно.
"""
        
        self._save_prompt("root_frame_prompt.txt", prompt)
    
    def _generate_parent_frame_prompt(self, frame_data: Dict[str, Any], frame_info: Dict[str, Any]):
        """Генерация промпта для родительского фрейма первого уровня"""
        prompt = f"""
# РОДИТЕЛЬСКИЙ ФРЕЙМ: {frame_data.get('name', 'N/A')}

## ОСНОВНАЯ ИНФОРМАЦИЯ:
- **Тип**: {frame_data.get('type', 'N/A')}
- **Размер**: {frame_data.get('size', {}).get('width', 0)} × {frame_data.get('size', {}).get('height', 0)} px
- **Непосредственных детей**: {frame_data.get('element_count', 0)}
- **Всего элементов (с вложенными)**: {frame_data.get('total_elements', 0)}
- **Положение в макете**: X: {frame_data.get('position', {}).get('x', 0)}, Y: {frame_data.get('position', {}).get('y', 0)}

## СТИЛИ ФРЕЙМА:
{self._format_frame_styles(frame_data.get('styles', {}))}

## ЛАЙАУТ НАСТРОЙКИ:
{self._format_frame_layout(frame_data.get('layout', {}))}

## ПОЛНАЯ СТРУКТУРА ФРЕЙМА (все вложенные элементы):
{self._format_complete_frame_structure(frame_data.get('children', []))}

## ДИЗАЙН-ТОКЕНЫ ФРЕЙМА:
{self._format_frame_design_tokens(frame_data.get('design_tokens', {}))}

## ГЛОБАЛЬНЫЕ ТОКЕНЫ:
{self._format_global_tokens(frame_data.get('global_design_tokens', {}))}

## ЗАДАЧА:
Создай самостоятельную секцию/компонент для этого родительского фрейма.
Реализуй ВСЮ структуру фрейма, включая все вложенные элементы.
Это основная секция макета, которая должна быть полностью функциональной.

## ОСОБЕННОСТИ РЕАЛИЗАЦИИ:
- Это родительский фрейм первого уровня (основная секция макета)
- Содержит {frame_data.get('total_elements', 0)} элементов включая все вложенные
- Должен быть семантически правильным HTML
- Должен использовать предоставленные дизайн-токены
- Должен быть адаптивным и переиспользуемым

## ВАЖНО:
Этот промпт содержит ПОЛНУЮ ИЕРАРХИЮ всех элементов этого фрейма.
Все дети, дети детей и т.д. уже включены в структуру.
Реализуй компонент ЦЕЛИКОМ на основе предоставленных данных.
"""
        
        filename = f"parent_frames/{frame_data['id']}_{self._sanitize_name(frame_data['name'])}_prompt.txt"
        self._save_prompt(filename, prompt)
    
    def _format_frame_styles(self, styles: Dict[str, Any]) -> str:
        """Форматирование стилей фрейма"""
        lines = []
        
        if styles.get('background'):
            lines.append(f"- **Фон**: `{styles['background']}`")
        
        border = styles.get('border', {})
        if border.get('color'):
            lines.append(f"- **Граница**: `{border['color']}`, {border.get('width', 0)}px")
        if border.get('radius', 0) > 0:
            lines.append(f"- **Border Radius**: {border['radius']}px")
        
        if styles.get('opacity', 1) < 1.0:
            lines.append(f"- **Прозрачность**: {styles['opacity']}")
        
        return "\n".join(lines) if lines else "Базовые стили (без особых настроек)"
    
    def _format_frame_layout(self, layout: Dict[str, Any]) -> str:
        """Форматирование лайаут настроек"""
        lines = []
        
        mode = layout.get('mode', 'NONE')
        if mode != 'NONE':
            lines.append(f"- **Режим лайаута**: {mode}")
        
        spacing = layout.get('spacing', 0)
        if spacing > 0:
            lines.append(f"- **Межэлементный spacing**: {spacing}px")
        
        padding = layout.get('padding', {})
        if any(padding.values()):
            lines.append(f"- **Padding**: L:{padding.get('left',0)} R:{padding.get('right',0)} T:{padding.get('top',0)} B:{padding.get('bottom',0)}px")
        
        constraints = layout.get('constraints', {})
        if constraints:
            lines.append(f"- **Констрейнты**: {constraints}")
        
        return "\n".join(lines) if lines else "Базовый лайаут"
    
    def _format_parent_frames_overview(self, children: List[Dict[str, Any]]) -> str:
        """Форматирование обзора родительских фреймов"""
        parent_frames = [child for child in children if child.get('type') == 'FRAME']
        
        if not parent_frames:
            return "Нет родительских фреймов первого уровня"
        
        lines = ["**Основные секции макета:**"]
        for i, frame in enumerate(parent_frames):
            total_elements = self._count_total_elements(frame)
            lines.append(f"{i+1}. **{frame.get('name', 'Unnamed')}**")
            lines.append(f"   - Размер: {frame.get('size', {}).get('width', 0)}×{frame.get('size', {}).get('height', 0)}px")
            lines.append(f"   - Элементов: {total_elements} (включая вложенные)")
            lines.append(f"   - Позиция: X:{frame.get('position', {}).get('x', 0)}, Y:{frame.get('position', {}).get('y', 0)}")
        
        return "\n".join(lines)
    
    def _list_parent_frames_names(self, children: List[Dict[str, Any]]) -> str:
        """Список имен родительских фреймов"""
        parent_frames = [child for child in children if child.get('type') == 'FRAME']
        
        if not parent_frames:
            return "Нет родительских фреймов"
        
        names = [f"- {frame.get('name', 'Unnamed')}" for frame in parent_frames]
        return "\n".join(names)
    
    def _format_complete_frame_structure(self, children: List[Dict[str, Any]], depth: int = 1) -> str:
        """Форматирование ПОЛНОЙ структуры фрейма"""
        if not children:
            return "Нет дочерних элементов"
        
        lines = []
        for child in children:
            indent = "  " * depth
            child_type = child.get('type', 'UNKNOWN')
            child_name = child.get('name', 'Unnamed')
            child_size = child.get('size', {})
            child_children_count = len(child.get('children', []))
            
            line = f"{indent}- **{child_type}**: {child_name}"
            line += f" ({child_size.get('width', 0)}×{child_size.get('height', 0)}px)"
            
            if child_children_count > 0:
                line += f" [детей: {child_children_count}]"
            
            # Стили элемента
            styles = child.get('styles', {})
            if styles.get('background'):
                line += f" | Фон: {styles['background']}"
            
            typography = styles.get('typography', {})
            if typography and typography.get('font_size'):
                line += f" | Текст: {typography.get('font_family', 'Inter')} {typography.get('font_size')}px"
            
            lines.append(line)
            
            # Рекурсивно добавляем всех детей (ПОЛНАЯ ВЛОЖЕННОСТЬ)
            if child.get('children'):
                lines.append(self._format_complete_frame_structure(child.get('children', []), depth + 1))
        
        return "\n".join(lines)
    
    def _format_frame_design_tokens(self, tokens: Dict[str, Any]) -> str:
        """Форматирование дизайн-токенов фрейма"""
        lines = []
        
        colors = tokens.get('colors', [])
        if colors:
            lines.append("**Цвета в этом фрейме:**")
            for color in colors[:8]:
                lines.append(f"- `{color}`")
        
        typography = tokens.get('typography', [])
        if typography:
            lines.append("\n**Типографика в этом фрейме:**")
            for i, typo in enumerate(typography[:4]):
                font_family = typo.get('font_family', 'Inter')
                font_size = typo.get('font_size', 16)
                font_weight = typo.get('font_weight', 400)
                lines.append(f"- Стиль {i+1}: {font_family} {font_size}px, вес {font_weight}")
        
        spacing = tokens.get('spacing', [])
        if spacing:
            lines.append("\n**Spacing значения:**")
            for space in spacing[:6]:
                lines.append(f"- `{space}px`")
        
        radius = tokens.get('border_radius', [])
        if radius:
            lines.append("\n**Border Radius значения:**")
            for rad in radius[:4]:
                lines.append(f"- `{rad}px`")
        
        return "\n".join(lines) if lines else "Используются в основном глобальные токены"
    
    def _format_global_tokens(self, tokens: Dict[str, Any]) -> str:
        """Форматирование глобальных токенов"""
        lines = []
        
        colors = tokens.get('colors', {})
        if colors:
            lines.append("**Основные цвета дизайн-системы:**")
            for name, color in list(colors.items())[:5]:
                lines.append(f"- `{name}`: `{color}`")
        
        typography = tokens.get('typography', {})
        if typography:
            lines.append("\n**Типографика дизайн-системы:**")
            for name, styles in list(typography.items())[:3]:
                lines.append(f"- `{name}`: {styles.get('font_family', 'Inter')} {styles.get('font_size', 16)}px")
        
        spacing = tokens.get('spacing', {})
        if spacing:
            lines.append("\n**Spacing система:**")
            for name, value in list(spacing.items())[:3]:
                lines.append(f"- `{name}`: `{value}`")
        
        radius = tokens.get('border_radius', {})
        if radius:
            lines.append("\n**Border Radius система:**")
            for name, value in list(radius.items())[:3]:
                lines.append(f"- `{name}`: `{value}`")
        
        return "\n".join(lines) if lines else "Глобальные токены не определены"
    
    def _count_total_elements(self, element: Dict[str, Any]) -> int:
        """Считаем общее количество элементов включая всех детей"""
        count = 1  # Сам элемент
        
        for child in element.get("children", []):
            count += self._count_total_elements(child)
        
        return count
    
    def _save_full_analysis(self, analysis: Dict[str, Any]):
        """Сохранение полного анализа"""
        json_file = os.path.join(self.output_dir, "complete_analysis_full.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"📊 Полный анализ: {json_file}")
    
    def _save_prompt(self, filename: str, content: str):
        """Сохранение промпта в файл"""
        filepath = os.path.join(self.prompts_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _create_smart_instructions(self, analysis: Dict[str, Any], frames_data: Dict[str, Any] = None):
        """Создание инструкции для умных промптов"""
        if frames_data:
            instructions = self._create_parent_frames_instructions(analysis, frames_data)
        else:
            instructions = self._create_legacy_instructions(analysis)
        
        self._save_prompt("SMART_INSTRUCTIONS.md", instructions)
    
    def _create_parent_frames_instructions(self, analysis: Dict[str, Any], frames_data: Dict[str, Any]) -> str:
        """Создание инструкции для системы с родительскими фреймами"""
        stats = analysis["statistics"]
        
        instructions = f"""
# УМНЫЕ ПРОМПТЫ ДЛЯ FIGMA МАКЕТА (РОДИТЕЛЬСКИЕ ФРЕЙМЫ)

## ОБЩАЯ ИНФОРМАЦИЯ:
- Всего элементов в анализе: {stats['total_elements']}
- Уровней вложенности: {stats['max_depth']}
- Всего фреймов: {frames_data['total_frames']}
- Родительских фреймов первого уровня: {len(frames_data['parent_frames'])}

## СТРУКТУРА ПРОМПТОВ:

### 📄 root_frame_prompt.txt - Корневой фрейм
- Основная структура всего макета
- Контейнер для родительских фреймов
- Обзор всех основных секций
- Всего элементов: {frames_data['root_frame']['total_elements']}

### 📁 parent_frames/ - Промпты для родительских фреймов
- Каждый файл - основная секция макета
- ПОЛНАЯ ВЛОЖЕННОСТЬ всех элементов секции
- Самодостаточные компоненты

## КЛЮЧЕВЫЕ ОСОБЕННОСТИ СИСТЕМЫ:

### 🎯 РОДИТЕЛЬСКИЕ ФРЕЙМЫ ПЕРВОГО УРОВНЯ
Система разделяет макет на основные секции:
{self._format_parent_frames_for_instructions(frames_data['parent_frames'])}

### 🚀 ПОЛНАЯ САМОДОСТАТОЧНОСТЬ
- Каждая секция реализуется независимо
- Все вложенные элементы уже включены в промпт
- Не нужно собирать информацию из разных источников

### 📊 ЛОГИЧЕСКОЕ РАЗДЕЛЕНИЕ
Макет разделен на {len(frames_data['parent_frames'])} основных секций,
каждая из которых содержит полную структуру своих элементов.

## ПОРЯДОК РАБОТЫ:
1. Начни с `root_frame_prompt.txt` - создай основную структуру-контейнер
2. Реализуй родительские фреймы из папки `parent_frames/` по одному
3. Каждая секция реализуется ЦЕЛИКОМ на основе своего промпта
4. Интегрируй готовые секции в корневую структуру

## ПРЕИМУЩЕСТВА СИСТЕМЫ:
- ✅ Логическое разделение макета на основные секции
- ✅ Управляемое количество промптов ({frames_data['total_frames']} вместо сотен)
- ✅ Каждый промпт содержит полную структуру своей секции
- ✅ Параллельная разработка разных секций
- ✅ Легкая интеграция готовых компонентов

## СОВЕТЫ ПО РЕАЛИЗАЦИИ:
- Внимательно изучи структуру каждой секции перед началом
- Используй семантические HTML теги для каждой секции
- Создай CSS-переменные для дизайн-токенов
- Тестируй каждую секцию отдельно перед интеграцией
- Сохраняй консистентность имен классов между секциями

Удачи в реализации! 🚀
"""
        
        return instructions

    def _format_parent_frames_for_instructions(self, parent_frames: List[Dict[str, Any]]) -> str:
        """Форматирование родительских фреймов для инструкции"""
        lines = []
        for frame in parent_frames:
            lines.append(f"- **{frame['name']}** - {frame['total_elements']} элементов")
        return "\n".join(lines)

    def _generate_legacy_prompts(self, analysis: Dict[str, Any]):
        """Старая логика для обратной совместимости"""
        print("⚠️  Используется устаревшая логика генерации промптов")
        # Простая реализация для обратной совместимости
        prompt = f"""
# ОСНОВНОЙ ПРОМПТ FIGMA МАКЕТА

## ОБЩАЯ ИНФОРМАЦИЯ:
- Всего элементов: {analysis['statistics']['total_elements']}
- Уровней вложенности: {analysis['statistics']['max_depth']}

## СТРУКТУРА:
{self._format_simple_structure(analysis['target_node'])}
"""
        self._save_prompt("legacy_main_prompt.txt", prompt)

    def _format_simple_structure(self, element: Dict[str, Any], depth: int = 0) -> str:
        """Простое форматирование структуры"""
        indent = "  " * depth
        lines = []
        
        lines.append(f"{indent}- {element.get('type')}: {element.get('name')}")
        
        for child in element.get('children', [])[:10]:  # Ограничиваем для читаемости
            lines.append(self._format_simple_structure(child, depth + 1))
        
        return "\n".join(lines)

    def _create_legacy_instructions(self, analysis: Dict[str, Any]) -> str:
        """Старая инструкция для обратной совместимости"""
        return """
# УСТАРЕВШАЯ СИСТЕМА ПРОМПТОВ

Эта система использует устаревший формат промптов.
Рекомендуется использовать систему с родительскими фреймами.
"""

    def _sanitize_name(self, name: str) -> str:
        """Очистка имени для файла"""
        return "".join(c if c.isalnum() else "_" for c in name.lower())[:30]