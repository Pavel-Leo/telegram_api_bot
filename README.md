## telegram_api_bot

```
Учебный проект телеграм-бот для отслеживания статуса проверки работы. Обрещение происходит к API Яндексa.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

Необходим токен от Яндекса
```

## Стек:
- Python 3.9
- python-telegram-bot 13.7

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Pavel-Leo/telegram_api_bot.git
```
cd Personal_diary_service
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv (для mac и linux)
python -m venv venv (для windows)
```

```
source venv/bin/activate (для mac и linux)
source venv/Scripts/activate (для windows)
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip (для mac и linux)
python -m pip install --upgrade pip (для windows)
```

```
перейти в дирректорию где хранится файл requirements.txt и оттуда выполнить команду:

pip install -r requirements.txt
```

##Запустить проект:

Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме

```
python homework.py
```
