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





# #########################################################
🤖 AI Agent Node
# Системный промпт:

CSS СТИЛИ:

css
/* CSS с дизайн-токенами */
.container {
  width: 100%;
  background: var(--color-primary);
}

.header {
  padding: var(--spacing-md);
}
JAVASCRIPT (если нужен):

javascript
// Интерактивность
document.addEventListener('DOMContentLoaded', function() {
  // код
});
⚡ ОСОБЫЕ ИНСТРУКЦИИ:
ПРИ ОБРАБОТКЕ КОРНЕВОГО ФРЕЙМА:
Создай основную HTML структуру

Определи CSS переменные для дизайн-токенов

Заложи основу для последующих секций

ПРИ ОБРАБОТКЕ КОНТЕЙНЕРА:
Создай контейнерную структуру

Реализуй layout систему

Подготовь места для вставки родительских фреймов

ПРИ ОБРАБОТКЕ РОДИТЕЛЬСКИХ ФРЕЙМОВ:
Каждая секция должна быть самодостаточной

Сохраняй семантическую структуру

Используй общие дизайн-токены

🛠 ИНСТРУМЕНТЫ:
process_figma_design
Назначение: Запуск анализа Figma макета

Параметры: figma_token, file_key, node_id

Результат: Генерация структуры промптов

get_next_prompt
Назначение: Получение следующего промпта в последовательности

Параметры: selected_frame (при выборе фрейма)

Результат: prompt_name, prompt_content, available_frames

💬 СТИЛЬ ОБЩЕНИЯ:
Будь вежливым и структурируй процесс

После каждого этапа подтверждай завершение

Четко объясняй что было сделано

Предлагай следующий шаг с четкими вариантами

При генерации кода - показывай реальный код, а не описание

🚀 ПОСЛЕДОВАТЕЛЬНОСТЬ ДИАЛОГА:
"Привет! Давай преобразуем Figma в код. Сначала нужен Figma API Token..."

"Токен получен! Теперь Figma File Key..."

"File Key есть! Теперь Node ID..."

"Все данные собраны! Запускаю анализ Figma..."

"Анализ завершен! Начинаем с корневого фрейма..."

[показывает код корневого фрейма]

"Переходим к контейнеру..."

[показывает код контейнера]

"Теперь выбери фрейм для обработки: [список]"

[обрабатывает выбранный фрейм, показывает код]

Повторяет шаги 9-10 пока не обработаны все фреймы

"Все фреймы обработаны! Код готов к использованию."

⚠️ ВАЖНЫЕ ПРАВИЛА:
НИКОГДА не пропускай этапы последовательности

ВСЕГДА показывай реальный код в ответ на промпты

ИСПОЛЬЗУЙ семантические HTML теги

ПРИМЕНЯЙ CSS переменные для дизайн-токенов

СОБЛЮДАЙ адаптивность и доступность

ОБЯЗАТЕЛЬНО подтверждай каждый завершенный этап

Твоя задача - быть проводником между Figma дизайном и готовым веб-кодом, четко следуя установленной последовательности!


### ############### ################

# ВОРКФЛОУ ДЛЯ N8N
Here's your workflow export in JSON format. You can import this into any n8n instance:

{
  "name": "Telegram Bot with OpenRouter AI Agent Integration",
  "nodes": [
    {
      "parameters": {
        "updates": [
          "message"
        ]
      },
      "id": "3f2bcd19-fc76-477b-bbdf-543d317d2cc4",
      "name": "Telegram Trigger",
      "type": "n8n-nodes-base.telegramTrigger",
      "typeVersion": 1.2,
      "position": [
        4592,
        1904
      ],
      "webhookId": "490579df-8e10-44ec-b2b8-b0282c40097d",
      "credentials": {
        "telegramApi": {
          "id": "RciuMnWIcjygiy0h",
          "name": "Telegram account"
        }
      }
    },
    {
      "parameters": {
        "model": "deepseek/deepseek-chat"
      },
      "id": "7e2ea0ba-2760-41b7-a1f1-517eb09059fc",
      "name": "OpenRouter Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenRouter",
      "typeVersion": 1,
      "position": [
        4768,
        2144
      ],
      "credentials": {
        "openRouterApi": {
          "id": "PuU8Yiwn2P1fUNv1",
          "name": "OpenRouter account 2"
        }
      }
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "={{ $json.message.text }}",
        "hasOutputParser": false,
        "options": {
          "systemMessage": "CSS СТИЛИ:\n\ncss\n/* CSS с дизайн-токенами */\n.container {\n  width: 100%;\n  background: var(--color-primary);\n}\n\n.header {\n  padding: var(--spacing-md);\n}\nJAVASCRIPT (если нужен):\n\njavascript\n// Интерактивность\ndocument.addEventListener('DOMContentLoaded', function() {\n  // код\n});\n⚡ ОСОБЫЕ ИНСТРУКЦИИ:\nПРИ ОБРАБОТКЕ КОРНЕВОГО ФРЕЙМА:\nСоздай основную HTML структуру\n\nОпредели CSS переменные для дизайн-токенов\n\nЗаложи основу для последующих секций\n\nПРИ ОБРАБОТКЕ КОНТЕЙНЕРА:\nСоздай контейнерную структуру\n\nРеализуй layout систему\n\nПодготовь места для вставки родительских фреймов\n\nПРИ ОБРАБОТКЕ РОДИТЕЛЬСКИХ ФРЕЙМОВ:\nКаждая секция должна быть самодостаточной\n\nСохраняй семантическую структуру\n\nИспользуй общие дизайн-токены\n\n🛠 ИНСТРУМЕНТЫ:\nprocess_figma_design\nНазначение: Запуск анализа Figma макета\n\nПараметры: figma_token, file_key, node_id\n\nРезультат: Генерация структуры промптов\n\nget_next_prompt\nНазначение: Получение следующего промпта в последовательности\n\nПараметры: selected_frame (при выборе фрейма)\n\nРезультат: prompt_name, prompt_content, available_frames\n\n💬 СТИЛЬ ОБЩЕНИЯ:\nБудь вежливым и структурируй процесс\n\nПосле каждого этапа подтверждай завершение\n\nЧетко объясняй что было сделано\n\nПредлагай следующий шаг с четкими вариантами\n\nПри генерации кода - показывай реальный код, а не описание\n\n🚀 ПОСЛЕДОВАТЕЛЬНОСТЬ ДИАЛОГА:\n\"Привет! Давай преобразуем Figma в код. Сначала нужен Figma API Token...\"\n\n\"Токен получен! Теперь Figma File Key...\"\n\n\"File Key есть! Теперь Node ID...\"\n\n\"Все данные собраны! Запускаю анализ Figma...\"\n\n\"Анализ завершен! Начинаем с корневого фрейма...\"\n\n[показывает код корневого фрейма]\n\n\"Переходим к контейнеру...\"\n\n[показывает код контейнера]\n\n\"Теперь выбери фрейм для обработки: [список]\"\n\n[обрабатывает выбранный фрейм, показывает код]\n\nПовторяет шаги 9-10 пока не обработаны все фреймы\n\n\"Все фреймы обработаны! Код готов к использованию.\"\n\n⚠️ ВАЖНЫЕ ПРАВИЛА:\nНИКОГДА не пропускай этапы последовательности\n\nВСЕГДА показывай реальный код в ответ на промпты\n\nИСПОЛЬЗУЙ семантические HTML теги\n\nПРИМЕНЯЙ CSS переменные для дизайн-токенов\n\nСОБЛЮДАЙ адаптивность и доступность\n\nОБЯЗАТЕЛЬНО подтверждай каждый завершенный этап\n\nТвоя задача - быть проводником между Figma дизайном и готовым веб-кодом, четко следуя установленной последовательности!"
        }
      },
      "id": "7d624a64-541f-45e0-85d5-db60818c686a",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 3,
      "position": [
        4936,
        1904
      ]
    },
    {
      "parameters": {
        "resource": "message",
        "operation": "sendMessage",
        "chatId": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
        "text": "={{ $json.formatted_text }}",
        "replyMarkup": "none",
        "additionalFields": {
          "disable_notification": true,
          "disable_web_page_preview": true
        }
      },
      "id": "6b7a8aa8-35f5-4de1-a191-af6783383654",
      "name": "Send Telegram Response",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1.2,
      "position": [
        5632,
        1904
      ],
      "webhookId": "e5bdfc59-900c-4db4-82f4-5b6641d72f3e",
      "credentials": {
        "telegramApi": {
          "id": "RciuMnWIcjygiy0h",
          "name": "Telegram account"
        }
      }
    },
    {
      "parameters": {
        "toolDescription": "Processes Figma design with provided API token, file key, and node ID. Returns generated code.",
        "method": "POST",
        "url": "https://python-figma.onrender.com/process",
        "sendBody": true,
        "contentType": "json",
        "specifyBody": "json",
        "jsonBody": "={{ {\"figma_token\": $fromAI(\"figma_token\", \"Figma API access token\"), \"file_key\": $fromAI(\"file_key\", \"Figma file key\"), \"node_id\": $fromAI(\"node_id\", \"Figma node ID\"), \"user_id\": $fromAI(\"user_id\", \"Telegram user ID\", \"string\", \"default_user\")} }}",
        "options": {
          "timeout": 120000
        }
      },
      "id": "dc5e706c-643c-4da1-941c-8888fef1f0a2",
      "name": "Call Python Script API",
      "type": "n8n-nodes-base.httpRequestTool",
      "typeVersion": 4.3,
      "position": [
        5088,
        2144
      ]
    },
    {
      "parameters": {
        "toolDescription": "Gets the next prompt file to process. Optionally accepts selected_frame parameter to get a specific frame prompt.",
        "method": "POST",
        "url": "https://python-figma.onrender.com/next_prompt",
        "sendBody": true,
        "contentType": "json",
        "specifyBody": "json",
        "jsonBody": "={{ {\"user_id\": $fromAI(\"user_id\", \"Telegram user ID\", \"string\", \"default_user\"), \"selected_frame\": $fromAI(\"selected_frame\", \"Selected frame name (optional)\", \"string\", \"\")} }}",
        "options": {
          "timeout": 120000
        }
      },
      "id": "8d8b27ae-30a0-4f6a-b15d-cf7591633c4f",
      "name": "Get Next Prompt",
      "type": "n8n-nodes-base.httpRequestTool",
      "typeVersion": 4.3,
      "position": [
        5248,
        2144
      ]
    },
    {
      "parameters": {
        "jsCode": "// Clean text for Telegram by removing markdown and problematic characters\nconst output = $input.item.json.output || '';\n\n// Remove markdown formatting\nlet cleanText = output\n  // Remove bold/italic markers\n  .replace(/\\*\\*/g, '')\n  .replace(/\\*/g, '')\n  .replace(/__/g, '')\n  .replace(/_/g, '')\n  // Remove code blocks\n  .replace(/```[\\s\\S]*?```/g, '')\n  .replace(/`/g, '')\n  // Remove HTML tags\n  .replace(/<[^>]*>/g, '')\n  // Remove links\n  .replace(/\\[([^\\]]+)\\]\\([^)]+\\)/g, '$1')\n  // Remove headers\n  .replace(/^#{1,6}\\s+/gm, '')\n  // Clean up multiple newlines\n  .replace(/\\n{3,}/g, '\\n\\n')\n  // Trim whitespace\n  .trim();\n\nreturn {\n  json: {\n    formatted_text: cleanText\n  }\n};"
      },
      "id": "cf55c2bf-d7bd-4433-b8cb-1b88b95a96a3",
      "name": "Format for Telegram",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [
        5408,
        1904
      ]
    },
    {
      "parameters": {
        "sessionIdType": "customKey",
        "sessionKey": "={{ $json.message.chat.id }}",
        "contextWindowLength": 5
      },
      "id": "a9a2e865-4c17-4e9a-a3f2-65cb7dd85c28",
      "name": "Simple Memory",
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "typeVersion": 1.3,
      "position": [
        4928,
        2144
      ]
    }
  ],
  "connections": {
    "Telegram Trigger": {
      "main": [
        [
          {
            "node": "AI Agent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenRouter Chat Model": {
      "ai_languageModel": [
        [
          {
            "node": "AI Agent",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    },
    "Call Python Script API": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    },
    "Get Next Prompt": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    },
    "AI Agent": {
      "main": [
        [
          {
            "node": "Format for Telegram",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Format for Telegram": {
      "main": [
        [
          {
            "node": "Send Telegram Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Simple Memory": {
      "ai_memory": [
        [
          {
            "node": "AI Agent",
            "type": "ai_memory",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {}
}
To import this workflow:

Copy the JSON above
In n8n, click the "+" button or go to Workflows
Click "Import from File" or "Import from URL"
Paste the JSON
Configure your credentials:
Telegram API (for Telegram Trigger and Send Telegram Response)
OpenRouter API (for OpenRouter Chat Model)

# ###################################################################



# render.com
ИСПРАВЬ НАСТРОЙКИ:
1. Start Command (ВАЖНО!):
Замени:

text
gunicorn your_application.wsgi
На:

text
python figma_bot_server.py
2. Environment Variables (добавь если нужно):
text
FIGMA_ACCESS_TOKEN=your_default_token_here
3. Build Command (оставь как есть):
text
pip install -r requirements.txt
📁 УБЕДИСЬ ЧТО В РЕПОЗИТОРИИ ЕСТЬ:
1. requirements.txt:
text
Flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
2. Обнови код сервера для работы на Render:
python
# В конец figma_bot_server.py добавь:
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Запуск Figma Bot Server на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
3. Создай файл runtime.txt (опционально):
text
python-3.9.13
🎯 ФИНАЛЬНЫЕ НАСТРОЙКИ ДЛЯ RENDER:
Name: python-figma ✓

Language: Python 3 ✓

Branch: main ✓

Region: Oregon ✓ (можно оставить)

Root Directory: (оставь пустым) ✓

Build Command: pip install -r requirements.txt ✓

Start Command: python figma_bot_server.py ← ИСПРАВЬ!

Instance Type: Free ✓

🚀 НАЖМИ "Create Web Service"
После деплоя ты получишь URL типа: https://python-figma.onrender.com

🔧 ДЛЯ N8N НАСТРОЙ:
URL: https://python-figma.onrender.com/process

URL: https://python-figma.onrender.com/next_prompt

⏰ ВАЖНО ДЛЯ FREE ТАРИФА:
Сервер "засыпает" после 15 минут неактивности

Первый запрос после простоя может занять 30-60 секунд

Perfect для тестирования!

Исправь Start Command и жми Create! 🚀