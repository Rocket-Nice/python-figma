ПОЛНАЯ ИНСТРУКЦИЯ ДЛЯ ЗАПУСКА FIGMA-TO-CODE СИСТЕМЫ
🛠 УСТАНОВКА И НАСТРОЙКА PYTHON
1. Установка зависимостей
bash
# Активация виртуального окружения (выбери подходящий вариант)
source venv3/bin/activate
# ИЛИ
source /home/max/bhp/venv3/bin/activate
# ИЛИ создай новое
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
2. Запуск основного скрипта (для тестирования)
bash
python main.py
Что делает: Запускает твой Figma-to-Code скрипт, который:

Подключается к Figma API

Анализирует дизайн

Создает папку generated_code/ с промптами

Генерирует smart_prompts/ с структурой фреймов

🚀 ЗАПУСК СЕРВЕРА ДЛЯ ТЕЛЕГРАМ БОТА
3. Запуск Flask сервера
bash
python figma_bot_server.py
Должен увидеть:

text
🚀 Запуск Figma Bot Server на http://localhost:5000
📁 Текущая директория: /home/max/Documents/petuhonizm/figma-to-code
 * Running on http://127.0.0.1:5000
4. Проверка работы сервера
Открой новый терминал и выполни:

bash
# Проверка статуса
curl http://localhost:5000/status

# Тест обработки Figma данных
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "figma_token": "test_token",
    "file_key": "test_file_key", 
    "node_id": "1619:4",
    "user_id": "test_user_123"
  }'
🔧 НАСТРОЙКА N8N WORKFLOW
5. Создай новый workflow в n8n с нодами:
📱 Telegram Trigger Node
Bot Token: 8502452188:AAHJGqKdW8wCkjRedBq8ekXWlbuKF7E3oGg

Update Type: Message

🤖 AI Agent Node
Системный промпт:

markdown
Ты - ассистент по преобразованию Figma в код с ПОСЛЕДОВАТЕЛЬНОЙ обработкой промптов. 

Общайся на РУССКОМ языке и управляй процессом поэтапно:

ЭТАП 1: Сбор данных Figma
1. Figma API Token
2. Figma File Key  
3. Figma Node ID

ЭТАП 2: Обработка промптов по порядку:
1. root_frame_prompt.txt (корневой фрейм)
2. root_container_prompt.txt (контейнер) 
3. Выбор фреймов из parent_frames/

Когда собрал все 3 параметра - вызови process_figma_design.
Когда нужно получить следующий промпт - вызови get_next_prompt.
Когда пользователь выбирает фрейм - передай в selected_frame.
Инструменты (Tools):

process_figma_design - для начальной обработки

get_next_prompt - для получения промптов

🌐 HTTP Request Node #1 - "Process Figma Data"
Method: POST

URL: http://localhost:5000/process

Headers: Content-Type: application/json

Body:

json
{
  "figma_token": "{{ $node.[AI Agent].json.figma_token }}",
  "file_key": "{{ $node.[AI Agent].json.file_key }}",
  "node_id": "{{ $node.[AI Agent].json.node_id }}",
  "user_id": "{{ $node.[Telegram Trigger].json.chatId }}"
}
🌐 HTTP Request Node #2 - "Get Next Prompt"
Method: POST

URL: http://localhost:5000/next_prompt

Headers: Content-Type: application/json

Body:

json
{
  "user_id": "{{ $node.[Telegram Trigger].json.chatId }}",
  "selected_frame": "{{ $node.[AI Agent].json.selected_frame }}"
}
💻 Code Node - "Process API Response"
javascript
const inputData = $input.all();
const response = inputData[0].json;

let result = {};

if (response.success) {
  if (response.prompt_content) {
    result = {
      hasPrompt: true,
      promptName: response.prompt_name,
      promptContent: response.prompt_content,
      nextStep: response.next_step,
      availableFrames: response.available_frames || null
    };
  } else if (response.available_frames) {
    result = {
      hasFramesList: true, 
      availableFrames: response.available_frames,
      message: response.message
    };
  } else {
    result = {
      success: true,
      message: response.message,
      nextStep: response.next_step
    };
  }
} else {
  result = {
    error: true,
    message: response.error || "Ошибка"
  };
}

return [result];
6. Схема подключения нод:
text
Telegram Trigger 
    ↓
AI Agent 
    ↓ (если вызван process_figma_design)
HTTP Request "Process Figma Data" 
    ↓  
Code "Process API Response"
    ↓
AI Agent
    ↓ (если вызван get_next_prompt) 
HTTP Request "Get Next Prompt"
    ↓
Code "Process API Response" 
    ↓
AI Agent
🧪 ТЕСТИРОВАНИЕ ПОЛНОЙ СИСТЕМЫ
7. Последовательность тестирования:
Запусти сервер: python figma_bot_server.py

Активируй workflow в n8n

Напиши боту в Telegram: "Привет"

Бот должен запросить:

Figma API Token

File Key

Node ID

После ввода данных: Бот обработает Figma и начнет последовательность промптов

8. Ожидаемый workflow диалога:
text
Пользователь: Привет
Бот: Привет! Давай преобразуем Figma в код. Сначала Figma API Token?

Пользователь: figd_123...
Бот: ✅ Токен получен! Теперь File Key?

Пользователь: ABC123...
Бот: ✅ File Key есть! Теперь Node ID?

Пользователь: 1619:4  
Бот: 🚀 Обрабатываю Figma дизайн...
[обработка через твой скрипт]
Бот: ✅ Готово! Начинаем генерацию кода.

🔹 ШАГ 1: Корневой фрейм...
[ИИ генерирует код по root_frame_prompt.txt]

🔹 ШАГ 2: Основной контейнер...
[ИИ генерирует код по root_container_prompt.txt]

🔹 ШАГ 3: Выбери фрейм для обработки:
1. Основная секция (1000001501)
2. Навигационная панель (1000001502)
3. Боковая панель (1000001544)

Пользователь: 1
Бот: 🔄 Обрабатываю основную секцию...
[ИИ генерирует код по выбранному промпту]
❗ УСТРАНЕНИЕ ПРОБЛЕМ
Если сервер не запускается:
bash
# Проверь зависимости
pip list | grep Flask

# Проверь порт
netstat -tulpn | grep 5000

# Если порт занят
pkill -f figma_bot_server
python figma_bot_server.py
Если n8n не соединяется с сервером:
Проверь что сервер запущен на http://localhost:5000

Проверь firewall настройки

Убедись что n8n и сервер на одной машине

Если не генерируются промпты:
Запусти python main.py отдельно для тестирования

Проверь что создается папка generated_code/

Убедись в правильности Figma данных

Теперь у тебя полная инструкция! Запускай и тестируй 🚀