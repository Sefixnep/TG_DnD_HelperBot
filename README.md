# DnD Master Assistant Telegram Bot

Этот проект представляет собой [Telegram бота](https://t.me/TG_DnD_HelperBot) для помощи мастеру игры Dungeons & Dragons, используя возможности ChatGPT. Бот предлагает простой и интуитивно понятный интерфейс, облегчая управление игровым процессом.

## Структура проекта

### `main.py`

Основной файл, в котором реализована логика работы бота. Здесь настроены основные команды, обработка сообщений и взаимодействие с пользователем.

### Папка `Auxiliary`

Вспомогательные файлы для поддержки функциональности бота.

- **`config.py`**: Хранит конфигурационные переменные, такие как ключи API для Telegram и ChatGPT, а также другие необходимые настройки.
  
- **`chat.py`**: Содержит структуру сообщений и кнопок на основе объектно-ориентированного программирования (ООП), обеспечивая удобство настройки и расширения функциональности бота.
  
- **`chatgpt.py`**: Класс для взаимодействия с ChatGPT, который обрабатывает запросы к API, упрощая и структурируя код.

## Установка и запуск

1. Клонируйте репозиторий:
   
    ```bash
    git clone https://github.com/your-repo/dnd-master-assistant.git
    ```
   
2. Установите зависимости:
   
    ```bash
    pip install -r requirements.txt
    ```

3. Настройте конфигурацию в `config.py`, добавив ключи API.

4. Запустите бота:
   
    ```bash
    python main.py
    ```

## Зависимости

Для корректной работы проекта необходимы следующие библиотеки:

- `pyTelegramBotAPI`
- `openai`

Все зависимости указаны в файле `requirements.txt`.
