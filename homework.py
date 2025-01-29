import sys
import logging
import time
from http import HTTPStatus

import requests
from telebot import TeleBot, apihelper

import exceptions as exc
from settings import (ENDPOINT, HEADERS, HOMEWORK_VERDICTS, PRACTICUM_TOKEN,
                      RETRY_PERIOD, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)


def check_tokens():
    """Проверяет наличие необходимых токенов для работы бота."""
    tokens = {
        'Токен Практикума': PRACTICUM_TOKEN,
        'Токен Бота': TELEGRAM_TOKEN,
        'ID чата': TELEGRAM_CHAT_ID,
    }
    result = []
    for name, token in tokens.items():
        if not token:
            result.append(name)
    if result:
        raise exc.TokenNotFoundException(result)


def send_message(bot: TeleBot, message: str):
    """Функция отправки сообщения."""
    try:
        logging.debug('Попытка отправки сообщения в Telegram...')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Удачная отправка сообщения в Telegram.')
        return True
    except (apihelper.ApiException,
            requests.exceptions.RequestException) as e:
        logging.error(f'Сбой при отправке сообщения в Telegram: {e}')
        return False


def get_api_answer(timestamp: time):
    """Получение ответа от API, приведение к типам данных Python."""
    payload = {'from_date': timestamp}
    try:
        api_args = {
            'URL': ENDPOINT,
            'Title': HEADERS,
            'Parametres': payload,
        }
        logging.debug(
            'Попытка запроса к API с данными:\n'
            'URL: {0}\n'
            'Title: {1}\n'
            'Parametres: {2}'.format(
                api_args['URL'],
                api_args['Title'],
                api_args['Parametres'],
            )
        )
        homework_statuses = requests.get(
            api_args['URL'],
            headers=api_args['Title'],
            params=api_args['Parametres'],
        )
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при попытке запроса к API: {e}')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise exc.ApiAnswerStatusCodeError(homework_statuses.status_code)
    return homework_statuses.json()


def check_response(response: dict):
    """Проверка на наличие ключей в ответе API."""
    if not isinstance(response, dict):
        response_type = type(response)
        raise exc.ApiResponseTypeError(response_type, dict)
    try:
        target_key = 'homeworks'
        homeworks = response[target_key]
    except KeyError:
        raise exc.ApiResponseAndParseKeyError(target_key, response)
    if not isinstance(homeworks, list):
        response_type = type(homeworks)
        raise exc.ApiResponseTypeError(response_type, list)
    return homeworks


def parse_status(homework: dict):
    """Извлекает из информации о конкретной домашней работе её статус."""
    try:
        target_key = 'homework_name'
        homework_name = homework[target_key]
    except KeyError:
        raise exc.ApiResponseAndParseKeyError(target_key, homework)
    try:
        target_key = 'status'
        verdict = homework[target_key]
    except KeyError:
        raise exc.ApiResponseAndParseKeyError(target_key, homework)
    if verdict not in HOMEWORK_VERDICTS:
        raise exc.WaitedHomeWorkVerdictError(verdict, HOMEWORK_VERDICTS)

    return (
        f'Изменился статус проверки работы "{homework_name}". '
        f'{HOMEWORK_VERDICTS[verdict]}'
    )


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = dict(homeworks[0])
                message = parse_status(homework)
                send_status = send_message(bot, message)
                if send_status is True:
                    timestamp = homework.get('current_date', timestamp)
                    last_message = ''
            else:
                logging.debug('Нет новых изменений в статусах.')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
            last_message = message
            if message != last_message:
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)

    logger.addHandler(stdout_handler)
    main()
