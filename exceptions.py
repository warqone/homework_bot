import logging


class TokenNotFoundException(Exception):
    """Не найдена одна или несколько переменных окружения."""

    def __init__(self, result):
        """Добавление ошибки в лог со списком не найденных токенов."""
        super().__init__(result)
        logging.critical((
            'Бот не  запущен, отсутствуют переменные окружения:'
            '\n' + '\n'.join(result)
        ))


class ApiAnswerStatusCodeError(Exception):
    """Статус-код ответа от API не соответствует ожидаемому."""

    def __init__(self, status_code):
        """Добавление ошибки в лог с возвращаемым status_code."""
        super().__init__(status_code)
        logging.error(
            f'Код ответа для запроса API {status_code}'
        )


class ApiResponseTypeError(TypeError):
    """API вернул не ожидаемый тип данных."""

    def __init__(self, response_type, waited_type):
        """Добавление ошибки в лог с возвращаемым и ожидаемым типом данных."""
        super().__init__(response_type, waited_type)
        logging.error(
            f'Ответ API вернул не ожидаемый тип данных: "{response_type}"'
            f'вместо "{waited_type}"'
        )


class ApiResponseAndParseKeyError(KeyError):
    """API вернул не ожидаемый набор ключей."""

    def __init__(self, waited_key, request_dict):
        """Добавление ошибки в лог с ожидаемым ключом и словарём."""
        super().__init__(waited_key, request_dict)
        logging.error(
            f'Отсутствует ожидаемый ключ {waited_key} в словаре:\n'
            f'{request_dict}'
        )


class WaitedHomeWorkVerdictError(ValueError):
    """Был получен вердикт которого нет в списке ожидаемых."""

    def __init__(self, verdict, homework_verdicts):
        """Добавление ошибки в лог с вердиктом и списком ожидаемых."""
        super().__init__(verdict, homework_verdicts)
        logging.error(
            f'Вердикт {verdict} отсутсвует в списке ожидаемых вердиктов:\n'
            f'{homework_verdicts}'
        )
