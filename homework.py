"""Код для телеграм бота.
Раз в 10 минут опрашивается API сервис Практикум.Домашка и проверяет статус
отправленной на ревью домашней работы.
При обновлении статуса анализируется ответ API и отправляется в чат
пользователя соответствующее уведомление в Telegram.
Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.
"""

import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exception import BotHomeworkException

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    filename="homework.log",
    filemode="w",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная необходимая для работы программы
    окружения — бот не должен запускаться.
    """
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def send_message(bot, message):
    """Отправляет сообщение в чат Telegram.
    Применяется каждый раз при обновлении статуса.
    """
    try:
        logger.debug("Сообщение отправляется.")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        logger.error(f"Не удалось отправить сообщение в чат. Ошибка: {error}")
        raise ValueError(f"Ошибка отправки сообщения в Telegram: {error}")
    else:
        logger.debug("Сообщение отправлено.")


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        logger.debug("Запрос на получение ответа от сервиса.")
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={"from_date": timestamp}
        )
    except Exception as error:
        logger.error(f"Не удалось получить ответ от сервиса. Ошибка: {error}")
        raise BotHomeworkException(
            "error", f"Не удалось получить ответ от сервиса. Ошибка: {error}"
        )
    else:
        if response.status_code != HTTPStatus.OK:
            logger.error(
                f"Не удалось получить ответ от сервиса. Статус код: "
                f"{response.status_code}"
            )
            raise BotHomeworkException(
                "error",
                f"Ошибка status_code: {response.status_code}",
            )
        return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(
            "error", "Не удалось получить ответ API в формате dict."
        )
    elif "homeworks" not in response or "current_date" not in response:
        logger.error("В ответе API нет ключей 'homeworks' или 'current_date'.")
        raise ValueError(
            "error",
            (
                "В словаре ответа от сервиса нет ключа 'homeworks' или"
                "'current_date'."
            ),
        )
    homeworks = response.get("homeworks")
    no_new_message = "Нет новых домашних работ."
    if not isinstance(homeworks, list):
        raise TypeError(
            "error",
            "В словаре ответа от сервиса ключ 'homeworks' не содержит список.",
        )
    if homeworks == []:
        logger.debug(no_new_message)
        message = no_new_message
    else:
        message = parse_status(homeworks[0])
    return message


def parse_status(homework):
    """Извлечение из полученной информации статуса домашней работы."""
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if "homework_name" not in homework:
        logger.error("Не удалось получить имя домашней работы.")
        raise KeyError(
            "В ответе от сервиса не содержится значение 'homework_name'."
        )
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error("Получен неизвестный статус для имени домашней работы.")
        raise BotHomeworkException(
            "error",
            f"Ответ содержит незадокументированный статус'{homework_status}'.",
        )
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    logger.debug(f"Извлечен статус домашней работы: {verdict}.")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical("Необходимо заполнить переменные окружения.")
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_message = ""
    while True:
        try:
            logger.info("Начало проверки нового статуса работы.")
            response = get_api_answer(timestamp)
            message = check_response(response)
            if previous_message != message:
                logger.info(
                    "Статус проверки работы изменился. Переход в "
                    "функцию send_message."
                )
                send_message(bot, message)
                previous_message = message
            else:
                logger.debug("Статус проверки работы не изменился.")
        except Exception as error:
            message = f"Что то пошло не так. Ошибка: {error}"
            logger.error(message)
        finally:
            if previous_message != message:
                previous_message = message
                send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
