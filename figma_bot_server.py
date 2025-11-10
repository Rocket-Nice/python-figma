# figma_bot_server_fixed.py
from flask import Flask, request, jsonify
import requests
import json
import os
import subprocess
import sys
from typing import Dict, Any, List

app = Flask(__name__)

# Хранилище состояний пользователей
user_sessions = {}

class FigmaBotProcessor:
    def __init__(self):
        self.output_dir = "generated_code"
    
    def process_figma_design(self, figma_token: str, file_key: str, node_id: str) -> Dict[str, Any]:
        """Запускает твой основной скрипт для обработки Figma"""
        try:
            print("🚀 Запускаем основной скрипт Figma-to-Code...")
            print(f"📊 Получены данные: {file_key}, нода: {node_id}")
            
            # Создаем временный .env файл с переданными данными
            env_content = f"""FIGMA_ACCESS_TOKEN={figma_token}
FIGMA_FILE_KEY={file_key}
FIGMA_NODE_ID={node_id}
"""
            
            with open(".temp_bot_env", "w") as f:
                f.write(env_content)
            
            # Запускаем твой основной скрипт
            result = subprocess.run([
                sys.executable, "main.py"
            ], capture_output=True, text=True, cwd=os.getcwd(), env={**os.environ, "FIGMA_ACCESS_TOKEN": figma_token, "FIGMA_FILE_KEY": file_key, "FIGMA_NODE_ID": node_id})
            
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
                error_msg = f"Ошибка выполнения скрипта: {result.stderr}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Ошибка при обработке: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False, 
                "error": error_msg
            }
        finally:
            # Удаляем временный файл
            if os.path.exists(".temp_bot_env"):
                os.remove(".temp_bot_env")
    
    def _read_generated_prompts(self) -> Dict[str, Any]:
        """Читает сгенерированные промпты из папки generated_code"""
        prompts_dir = os.path.join(self.output_dir, "smart_prompts")
        
        if not os.path.exists(prompts_dir):
            return {"error": "Папка с промптами не найдена"}
        
        structure = {
            "root_frame": {
                "name": "root_frame_prompt.txt",
                "file_path": os.path.join(prompts_dir, "root_frame_prompt.txt"),
                "description": "Корневой фрейм - основная структура всего макета",
                "order": 1
            },
            "container": {
                "name": "root_container_prompt.txt",
                "file_path": os.path.join(prompts_dir, "parent_frames", "root_container_prompt.txt"), 
                "description": "Основной контейнер для родительских фреймов",
                "order": 2
            },
            "parent_frames": []
        }
        
        # Добавляем родительские фреймы
        parent_frames_dir = os.path.join(prompts_dir, "parent_frames")
        if os.path.exists(parent_frames_dir):
            for filename in os.listdir(parent_frames_dir):
                if filename.endswith("_prompt.txt") and filename != "root_container_prompt.txt":
                    frame_id = filename.replace("_prompt.txt", "").replace("root_frame_", "")
                    structure["parent_frames"].append({
                        "name": filename,
                        "file_path": os.path.join(parent_frames_dir, filename),
                        "description": f"Фрейм {frame_id}",
                        "order": len(structure["parent_frames"]) + 3
                    })
        
        return structure
    
    def _get_available_frames(self) -> List[Dict[str, str]]:
        """Список доступных фреймов для выбора"""
        prompts_dir = os.path.join(self.output_dir, "smart_prompts", "parent_frames")
        frames = []
        
        if os.path.exists(prompts_dir):
            for filename in os.listdir(prompts_dir):
                if filename.endswith("_prompt.txt"):
                    frame_id = filename.replace("_prompt.txt", "").replace("root_frame_", "")
                    frames.append({
                        "id": frame_id,
                        "name": filename,
                        "description": f"Фрейм {frame_id}"
                    })
        
        return frames
    
    def get_prompt_content(self, prompt_name: str) -> str:
        """Получение содержимого промпта по имени"""
        try:
            # Ищем файл в разных возможных местах
            possible_paths = [
                os.path.join(self.output_dir, "smart_prompts", prompt_name),
                os.path.join(self.output_dir, "smart_prompts", "parent_frames", prompt_name),
                os.path.join("generated_code", "smart_prompts", prompt_name),
                os.path.join("generated_code", "smart_prompts", "parent_frames", prompt_name)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"✅ Прочитан промпт: {path} ({len(content)} символов)")
                        return content
            
            return f"❌ Промпт {prompt_name} не найден. Доступные пути: {possible_paths}"
            
        except Exception as e:
            return f"❌ Ошибка чтения промпта: {str(e)}"

# Инициализация процессора
processor = FigmaBotProcessor()

@app.route('/process', methods=['POST'])
def process_figma():
    """Основная конечная точка для обработки Figma данных"""
    try:
        data = request.json
        figma_token = data.get('figma_token')
        file_key = data.get('file_key')
        node_id = data.get('node_id')
        user_id = data.get('user_id', 'default_user')
        
        print(f"📥 Получен POST запрос на /process от пользователя {user_id}")
        print(f"   File Key: {file_key}")
        print(f"   Node ID: {node_id}")
        print(f"   Token: {figma_token[:20]}...")
        
        # Инициализируем сессию пользователя
        user_sessions[user_id] = {
            "current_step": "root_frame",
            "processed_prompts": [],
            "available_frames": processor._get_available_frames(),
            "figma_data": {"token": figma_token, "file_key": file_key, "node_id": node_id}
        }
        
        # Вызываем основную функцию обработки
        result = processor.process_figma_design(figma_token, file_key, node_id)
        
        response_data = {
            "success": result["success"],
            "result": result,
            "next_step": "root_frame_prompt.txt",
            "message": "Данные Figma обработаны! Начинаем с корневого фрейма."
        }
        
        if not result["success"]:
            response_data["error"] = result["error"]
        
        print(f"📤 Отправляем ответ: {response_data['success']}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Ошибка в /process: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/next_prompt', methods=['POST'])
def get_next_prompt():
    """Получение следующего промпта в последовательности"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        selected_frame = data.get('selected_frame')
        
        print(f"📥 Получен POST запрос на /next_prompt от {user_id}")
        print(f"   Selected frame: {selected_frame}")
        
        session = user_sessions.get(user_id)
        if not session:
            return jsonify({"success": False, "error": "Сессия не найдена. Начните с /start"}), 400
        
        # Определяем следующий промпт на основе текущего шага
        next_prompt_name = None
        next_step_description = ""
        
        if session["current_step"] == "root_frame":
            next_prompt_name = "root_frame_prompt.txt"
            session["current_step"] = "container"
            next_step_description = "root_container_prompt.txt"
            
        elif session["current_step"] == "container":
            next_prompt_name = "root_container_prompt.txt"
            session["current_step"] = "parent_frames"
            next_step_description = "выбор фрейма из parent_frames"
            
        elif session["current_step"] == "parent_frames" and selected_frame:
            next_prompt_name = selected_frame
            session["processed_prompts"].append(selected_frame)
            next_step_description = "следующий фрейм из parent_frames"
            
        else:
            return jsonify({
                "success": False, 
                "error": "Неопределенное состояние или не выбран фрейм"
            }), 400
        
        # Получаем содержимое промпта
        prompt_content = processor.get_prompt_content(next_prompt_name)
        
        session["processed_prompts"].append(next_prompt_name)
        
        response_data = {
            "success": True,
            "prompt_name": next_prompt_name,
            "prompt_content": prompt_content,
            "next_step": next_step_description,
            "processed_count": len(session["processed_prompts"])
        }
        
        # Если переходим к выбору фреймов, добавляем список доступных
        if session["current_step"] == "parent_frames":
            response_data["available_frames"] = session["available_frames"]
        
        print(f"📤 Отправляем промпт: {next_prompt_name}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Ошибка в /next_prompt: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/available_frames', methods=['GET'])
def get_available_frames():
    """Получение списка доступных фреймов"""
    user_id = request.args.get('user_id', 'default_user')
    session = user_sessions.get(user_id)
    
    if not session:
        return jsonify({"success": False, "error": "Сессия не найдена"}), 400
    
    return jsonify({
        "success": True,
        "available_frames": session["available_frames"]
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Проверка статуса сервера"""
    user_id = request.args.get('user_id', 'default_user')
    session = user_sessions.get(user_id)
    
    status_info = {
        "server": "running",
        "host": "localhost:5000", 
        "user_session_exists": session is not None
    }
    
    if session:
        status_info.update({
            "current_step": session["current_step"],
            "processed_prompts": session["processed_prompts"],
            "available_frames_count": len(session["available_frames"])
        })
    
    return jsonify(status_info)

@app.route('/test', methods=['GET'])
def test_connection():
    """Простой тест соединения"""
    return jsonify({
        "status": "ok",
        "message": "Сервер работает корректно",
        "timestamp": "2025-11-10 16:00:00"
    })

if __name__ == '__main__':
    # print("🚀 Запуск Figma Bot Server на http://localhost:5000")
    # print("📁 Текущая директория:", os.getcwd())
    # print("🔧 Режим: DEBUG")
    
    # # Запускаем на localhost только
    # app.run(host='127.0.0.1', port=5000, debug=True)

    # ...
    print("🚀 Запуск Figma Bot Server на http://0.0.0.0:80")
    print("📁 Текущая директория:", os.getcwd())
    
    # Запускаем на порту 80 (стандартный HTTP порт)
    app.run(host='0.0.0.0', port=8080, debug=True)