class TokenNotFoundException(Exception):
    """Не найдена одна или несколько переменных окружения."""


class RequestApiError(Exception):
    """Ошибка при попытке запроса к API."""


class ApiAnswerStatusCodeError(Exception):
    """Статус-код ответа от API не соответствует ожидаемому."""


class ApiResponseTypeError(TypeError):
    """API вернул не ожидаемый тип данных."""


class ApiResponseAndParseKeyError(KeyError):
    """API вернул не ожидаемый набор ключей."""


class WaitedHomeWorkVerdictError(ValueError):
    """Был получен вердикт которого нет в списке ожидаемых."""
