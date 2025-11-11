# figma_bot_server_fixed.py
from flask import Flask, request, jsonify
import requests
import json
import os
import subprocess
import sys
from typing import Dict, Any, List

# Создаем Flask приложение - веб-сервер для API
app = Flask(__name__)

# Хранилище состояний пользователей (в памяти)
# В реальном приложении лучше использовать базу данных
user_sessions = {}

class FigmaBotProcessor:
    """
    Обработчик Figma дизайнов - координирует работу всей системы
    через веб-интерфейс
    """
    
    def __init__(self):
        self.output_dir = "generated_code"
    
    def process_figma_design(self, figma_token: str, file_key: str, node_id: str) -> Dict[str, Any]:
        """
        Основной метод - запускает процесс обработки Figma дизайна
        Возвращает структуру промптов для последовательной обработки
        """
        try:
            print("🚀 Запускаем основной скрипт Figma-to-Code...")
            print(f"📊 Получены данные: {file_key}, нода: {node_id}")
            
            # Создаем временный .env файл с переданными данными
            # Это нужно потому что основной скрипт читает конфиг из .env
            env_content = f"""FIGMA_ACCESS_TOKEN={figma_token}
FIGMA_FILE_KEY={file_key}
FIGMA_NODE_ID={node_id}
"""
            
            # Сохраняем временный файл с настройками
            with open(".temp_bot_env", "w") as f:
                f.write(env_content)
            
            # ЗАПУСКАЕМ ОСНОВНОЙ СКРИПТ КАК ПОДПРОЦЕСС
            # Это позволяет изолировать выполнение и перехватывать вывод
            result = subprocess.run([
                sys.executable, "main.py"  # Запускаем main.py
            ], 
            capture_output=True,    # Перехватываем stdout и stderr
            text=True,              # Возвращаем строки вместо bytes
            cwd=os.getcwd(),        # Рабочая директория - текущая
            env={**os.environ,      # Передаем переменные окружения + наши
                 "FIGMA_ACCESS_TOKEN": figma_token, 
                 "FIGMA_FILE_KEY": file_key, 
                 "FIGMA_NODE_ID": node_id}
            )
            
            # Проверяем успешность выполнения
            if result.returncode == 0:
                print("✅ Основной скрипт выполнен успешно")
                
                # Читаем сгенерированную структуру промптов
                prompt_structure = self._read_generated_prompts()
                
                return {
                    "success": True,
                    "message": "Figma дизайн успешно обработан! Сгенерированы промпты для последовательной обработки.",
                    "prompt_structure": prompt_structure,
                    "available_frames": self._get_available_frames(),
                    "script_output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
                }
            else:
                # Если скрипт завершился с ошибкой
                error_msg = f"Ошибка выполнения скрипта: {result.stderr}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            # Обрабатываем любые исключения
            error_msg = f"Ошибка при обработке: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False, 
                "error": error_msg
            }
        finally:
            # Удаляем временный файл в любом случае
            if os.path.exists(".temp_bot_env"):
                os.remove(".temp_bot_env")
    
    def _read_generated_prompts(self) -> Dict[str, Any]:
        """
        Читает сгенерированные промпты из папки generated_code
        Создает структуру для навигации по промптам
        """
        prompts_dir = os.path.join(self.output_dir, "smart_prompts")
        
        if not os.path.exists(prompts_dir):
            return {"error": "Папка с промптами не найдена"}
        
        # СТРУКТУРА ПРОМПТОВ ДЛЯ ПОСЛЕДОВАТЕЛЬНОЙ ОБРАБОТКИ
        structure = {
            "root_frame": {
                "name": "root_frame_prompt.txt",
                "file_path": os.path.join(prompts_dir, "root_frame_prompt.txt"),
                "description": "Корневой фрейм - основная структура всего макета",
                "order": 1  # Порядок обработки
            },
            "container": {
                "name": "root_container_prompt.txt", 
                "file_path": os.path.join(prompts_dir, "parent_frames", "root_container_prompt.txt"),
                "description": "Основной контейнер для родительских фреймов",
                "order": 2
            },
            "parent_frames": []  # Список родительских фреймов
        }
        
        # Добавляем родительские фреймы из папки parent_frames
        parent_frames_dir = os.path.join(prompts_dir, "parent_frames")
        if os.path.exists(parent_frames_dir):
            for filename in os.listdir(parent_frames_dir):
                # Ищем файлы промптов (заканчиваются на _prompt.txt)
                if filename.endswith("_prompt.txt") and filename != "root_container_prompt.txt":
                    # Извлекаем ID фрейма из имени файла
                    frame_id = filename.replace("_prompt.txt", "").replace("root_frame_", "")
                    structure["parent_frames"].append({
                        "name": filename,
                        "file_path": os.path.join(parent_frames_dir, filename),
                        "description": f"Фрейм {frame_id}",
                        "order": len(structure["parent_frames"]) + 3  # Порядок после корня и контейнера
                    })
        
        return structure
    
    def _get_available_frames(self) -> List[Dict[str, str]]:
        """
        Возвращает список доступных фреймов для выбора пользователем
        """
        prompts_dir = os.path.join(self.output_dir, "smart_prompts", "parent_frames")
        frames = []
        
        if os.path.exists(prompts_dir):
            for filename in os.listdir(prompts_dir):
                if filename.endswith("_prompt.txt"):
                    # Извлекаем информацию о фрейме из имени файла
                    frame_id = filename.replace("_prompt.txt", "").replace("root_frame_", "")
                    frames.append({
                        "id": frame_id,
                        "name": filename,
                        "description": f"Фрейм {frame_id}"
                    })
        
        return frames
    
    def get_prompt_content(self, prompt_name: str) -> str:
        """
        Получает содержимое промпта по имени файла
        Ищет файл в разных возможных местах
        """
        try:
            # ВОЗМОЖНЫЕ ПУТИ К ФАЙЛАМ ПРОМПТОВ
            possible_paths = [
                os.path.join(self.output_dir, "smart_prompts", prompt_name),
                os.path.join(self.output_dir, "smart_prompts", "parent_frames", prompt_name),
                os.path.join("generated_code", "smart_prompts", prompt_name),
                os.path.join("generated_code", "smart_prompts", "parent_frames", prompt_name)
            ]
            
            # Пробуем найти файл по каждому пути
            for path in possible_paths:
                if os.path.exists(path):
                    # Читаем содержимое файла
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"✅ Прочитан промпт: {path} ({len(content)} символов)")
                        return content
            
            # Если файл не найден ни по одному пути
            return f"❌ Промпт {prompt_name} не найден. Доступные пути: {possible_paths}"
            
        except Exception as e:
            return f"❌ Ошибка чтения промпта: {str(e)}"

# Инициализация процессора (создаем один экземпляр)
processor = FigmaBotProcessor()

# 📍 ROUTE 1: ОСНОВНАЯ КОНЕЧНАЯ ТОЧКА ДЛЯ ОБРАБОТКИ FIGMA
@app.route('/process', methods=['POST'])
def process_figma():
    """
    Основной endpoint для начала обработки Figma дизайна
    Принимает данные Figma и запускает процесс анализа
    """
    try:
        # Получаем JSON данные из запроса
        data = request.json
        figma_token = data.get('figma_token')  # Токен доступа Figma
        file_key = data.get('file_key')        # ID файла Figma
        node_id = data.get('node_id')          # ID конкретной ноды
        user_id = data.get('user_id', 'default_user')  # ID пользователя для сессии
        
        print(f"📥 Получен POST запрос на /process от пользователя {user_id}")
        print(f"   File Key: {file_key}")
        print(f"   Node ID: {node_id}")
        print(f"   Token: {figma_token[:20]}...")  # Логируем только начало токена
        
        # ИНИЦИАЛИЗИРУЕМ СЕССИЮ ПОЛЬЗОВАТЕЛЯ
        # Сохраняем состояние обработки для этого пользователя
        user_sessions[user_id] = {
            "current_step": "root_frame",      # Текущий этап обработки
            "processed_prompts": [],           # Список обработанных промптов
            "available_frames": processor._get_available_frames(),  # Доступные фреймы
            "figma_data": {"token": figma_token, "file_key": file_key, "node_id": node_id}
        }
        
        # ВЫЗЫВАЕМ ОСНОВНУЮ ФУНКЦИЮ ОБРАБОТКИ
        result = processor.process_figma_design(figma_token, file_key, node_id)
        
        # ФОРМИРУЕМ ОТВЕТ
        response_data = {
            "success": result["success"],
            "result": result,
            "next_step": "root_frame_prompt.txt",  # Следующий шаг для клиента
            "message": "Данные Figma обработаны! Начинаем с корневого фрейма."
        }
        
        # Добавляем ошибку если процесс не удался
        if not result["success"]:
            response_data["error"] = result["error"]
        
        print(f"📤 Отправляем ответ: {response_data['success']}")
        return jsonify(response_data)
        
    except Exception as e:
        # ОБРАБОТКА ОШИБОК СЕРВЕРА
        error_msg = f"Ошибка в /process: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500  # HTTP 500 - Internal Server Error

# 📍 ROUTE 2: ПОЛУЧЕНИЕ СЛЕДУЮЩЕГО ПРОМПТА
@app.route('/next_prompt', methods=['POST'])
def get_next_prompt():
    """
    Endpoint для получения следующего промпта в последовательности
    Клиент запрашивает следующий промпт после обработки предыдущего
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        selected_frame = data.get('selected_frame')  # Если пользователь выбрал конкретный фрейм
        
        # ПРОВЕРЯЕМ СЕССИЮ ПОЛЬЗОВАТЕЛЯ
        session = user_sessions.get(user_id)
        if not session:
            return jsonify({"success": False, "error": "Сессия не найдена"}), 400
        
        # ОПРЕДЕЛЯЕМ СЛЕДУЮЩИЙ ПРОМПТ НА ОСНОВЕ ТЕКУЩЕГО ЭТАПА
        next_prompt_name = None
        
        if session["current_step"] == "root_frame":
            # Первый шаг - корневой фрейм
            next_prompt_name = "root_frame_prompt.txt"
            session["current_step"] = "container"
            
        elif session["current_step"] == "container":
            # Второй шаг - контейнер
            next_prompt_name = "root_container_prompt.txt"
            session["current_step"] = "parent_frames"
            
        elif session["current_step"] == "parent_frames" and selected_frame:
            # Третий шаг - выбранный родительский фрейм
            next_prompt_name = selected_frame
            session["processed_prompts"].append(selected_frame)
        
        # ВАЖНО: Получаем РЕАЛЬНОЕ содержимое промпта
        prompt_content = processor.get_prompt_content(next_prompt_name)
        
        # Если контент не найден, возвращаем ошибку
        if "❌" in prompt_content:
            return jsonify({
                "success": False,
                "error": f"Не удалось прочитать промпт: {prompt_content}"
            }), 400
        
        # ОБНОВЛЯЕМ СЕССИЮ ПОЛЬЗОВАТЕЛЯ
        session["processed_prompts"].append(next_prompt_name)
        
        # ФОРМИРУЕМ ОТВЕТ
        response_data = {
            "success": True,
            "prompt_name": next_prompt_name,
            "prompt_content": prompt_content,  # ← ВОТ ЭТО ВАЖНО! Сам текст промпта
            "next_step": "обработка промпта ИИ",
            "processed_count": len(session["processed_prompts"])
        }
        
        # Если переходим к выбору фреймов, добавляем список доступных
        if session["current_step"] == "parent_frames":
            response_data["available_frames"] = session["available_frames"]
        
        print(f"📤 Отправляем промпт: {next_prompt_name} ({len(prompt_content)} символов)")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Ошибка в /next_prompt: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

# 📍 ROUTE 3: ПОЛУЧЕНИЕ СПИСКА ДОСТУПНЫХ ФРЕЙМОВ
@app.route('/available_frames', methods=['GET'])
def get_available_frames():
    """Получение списка доступных фреймов для пользователя"""
    user_id = request.args.get('user_id', 'default_user')
    session = user_sessions.get(user_id)
    
    if not session:
        return jsonify({"success": False, "error": "Сессия не найдена"}), 400
    
    return jsonify({
        "success": True,
        "available_frames": session["available_frames"]
    })

# 📍 ROUTE 4: ПРОВЕРКА СТАТУСА СЕРВЕРА
@app.route('/status', methods=['GET'])
def get_status():
    """Проверка статуса сервера и пользовательской сессии"""
    user_id = request.args.get('user_id', 'default_user')
    session = user_sessions.get(user_id)
    
    status_info = {
        "server": "running",
        "host": "localhost:5000", 
        "user_session_exists": session is not None
    }
    
    # Добавляем информацию о сессии если она есть
    if session:
        status_info.update({
            "current_step": session["current_step"],
            "processed_prompts": session["processed_prompts"],
            "available_frames_count": len(session["available_frames"])
        })
    
    return jsonify(status_info)

# 📍 ROUTE 5: ПРОСТОЙ ТЕСТ СОЕДИНЕНИЯ
@app.route('/test', methods=['GET'])
def test_connection():
    """Простой тест для проверки что сервер работает"""
    return jsonify({
        "status": "ok",
        "message": "Сервер работает корректно",
        "timestamp": "2025-11-10 16:00:00"
    })

# 🚀 ЗАПУСК СЕРВЕРА
if __name__ == '__main__':
    # Динамический порт (для deployment на Heroku, Railway и т.д.)
    port = int(os.environ.get('PORT', 5000))  # Берем порт из переменной окружения или 5000 по умолчанию
    
    print(f"🚀 Запуск Figma Bot Server на порту {port}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    print(f"🔧 Режим: {'DEBUG' if os.environ.get('DEBUG') else 'PRODUCTION'}")
    
    # Запускаем сервер
    # host='0.0.0.0' - слушаем все интерфейсы
    # port=port - порт из переменной окружения
    # debug=False - в продакшне debug должен быть выключен
    app.run(host='0.0.0.0', port=port, debug=False)