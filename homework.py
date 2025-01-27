import logging
import sys
import time

import requests
from telebot import TeleBot

from settings import (ENDPOINT, HEADERS, HOMEWORK_VERDICTS, PRACTICUM_TOKEN,
                      RETRY_PERIOD, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)


def check_tokens():
    """Проверяет наличие необходимых токенов для работы бота."""
    practicum_token = PRACTICUM_TOKEN
    telegram_token = TELEGRAM_TOKEN
    telegram_chat_id = TELEGRAM_CHAT_ID

    if not practicum_token or not telegram_token or not telegram_chat_id:
        logging.critical(
            'Отсутствует какая-то из переменных окружения — продолжать '
            'работу бота нет смысла.'
        )
        sys.exit()
    return True


def send_message(bot: TeleBot, message: str):
    """Функция отправки сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Удачная отправка сообщения в Telegram.')
    except Exception as e:
        logging.error(f'Сбой при отправке сообщения в Telegram: {e}')


def get_api_answer(timestamp: time):
    """Получение ответа от API, приведение к типам данных Python."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload
        )
        if homework_statuses.status_code != 200:
            logging.error(
                f'Код ответа для запроса API {homework_statuses.url}'
            )
            return False
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при попытке запроса к API: {e}')


def check_response(response: dict):
    """Проверка на наличие ключей в ответе API."""
    if not isinstance(response, dict):
        logging.error(TypeError, 'Ответ API вернул не словарь.')

    try:
        homeworks = response['homeworks']
    except KeyError:
        logging.error(
            KeyError,
            'Отсутствуют ожидаемые ключи "homeworks" и "current_date" '
            'в ответе API.'
        )

    if isinstance(homeworks, list):
        return homeworks
    else:
        logging.error(
            TypeError,
            'Данные под ключом "homeworks" вернули не список.'
        )


def parse_status(homework: dict):
    """Извлекает из информации о конкретной домашней работе её статус."""
    try:
        homework_name = homework['homework_name']
        verdict = homework['status']
    except KeyError:
        logging.error(
            KeyError,
            'Отсутствует ключ "status" или "homework_name" '
            'в информации о домашней работе'
        )

    if verdict not in HOMEWORK_VERDICTS:
        logging.error(ValueError, 'Был получен неизвестный статус вердикта.')

    return (
        f'Изменился статус проверки работы "{homework_name}". '
        f'{HOMEWORK_VERDICTS[verdict]}'
    )


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
            else:
                logging.debug('Нет новых изменений в статусах.')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
