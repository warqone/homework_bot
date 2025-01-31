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
        message = (
            'Бот не  запущен, отсутствуют переменные окружения:'
            '\n' + '\n'.join(result)
        )
        logging.critical(message)
        raise exc.TokenNotFoundException(message)


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
            'url': ENDPOINT,
            'headers': HEADERS,
            'params': payload,
        }
        logging.debug(
            'Попытка запроса к API с данными:\n'
            'URL: {url}\n'
            'Headers: {headers}\n'
            'Parametres: {params}'.format(**api_args)
        )
        homework_statuses = requests.get(**api_args)
    except requests.exceptions.RequestException as e:
        message = (
            f'Возникла ошибка при попытке запроса к API: {e},'
        )
        logging.error(message)
        raise exc.RequestApiError(message)
    if homework_statuses.status_code != HTTPStatus.OK:
        message = (
            f'Код ответа от API: {homework_statuses.status_code} - '
            'не соответствует ожидаемому.'
        )
        logging.error(message)
        raise exc.ApiAnswerStatusCodeError(message)
    return homework_statuses.json()


def check_response(response: dict):
    """Проверка на наличие ключей в ответе API."""
    if not isinstance(response, dict):
        response_type = type(response)
        message = (
            f'Ответ API вернул не ожидаемый тип данных: "{response_type}"'
            f'вместо "{dict}"'
        )
        logging.error(message)
        raise exc.ApiResponseTypeError(message)
    try:
        target_key = 'homeworks'
        homeworks = response[target_key]
    except KeyError:
        message = (
            f'Отсутствует ожидаемый ключ {target_key} в словаре: '
            f'{homeworks}'
        )
        logging.error(message)
        raise exc.ApiResponseAndParseKeyError(message)
    if not isinstance(homeworks, list):
        response_type = type(homeworks)
        message = (
            f'Ответ API вернул не ожидаемый тип данных: "{response_type}"'
            f'вместо "{dict}"'
        )
        logging.error(message)
        raise exc.ApiResponseTypeError(message)
    return homeworks


def parse_status(homework: dict):
    """Извлекает из информации о конкретной домашней работе её статус."""
    try:
        target_key = 'homework_name'
        homework_name = homework[target_key]
    except KeyError:
        message = (
            f'Отсутствует ожидаемый ключ {target_key} в словаре: '
            f'{homework}'
        )
        logging.error(message)
        raise exc.ApiResponseAndParseKeyError(message)
    try:
        target_key = 'status'
        verdict = homework[target_key]
    except KeyError:
        message = (
            f'Отсутствует ожидаемый ключ {target_key} в словаре: '
            f'{homework}'
        )
        logging.error(message)
        raise exc.ApiResponseAndParseKeyError(message)
    if verdict not in HOMEWORK_VERDICTS:
        message = (
            f'Вердикт {verdict} отсутсвует в списке ожидаемых вердиктов:\n'
            f'{HOMEWORK_VERDICTS}'
        )
        logging.error(message)
        raise exc.WaitedHomeWorkVerdictError(message)

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
                if send_status:
                    timestamp = homework.get('current_date', timestamp)
                    last_message = ''
            else:
                logging.debug('Нет новых изменений в статусах.')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
            if message != last_message:
                last_message = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    main()
