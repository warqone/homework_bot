class TokenNotFoundException(Exception):
    """Не найдена одна или несколько переменных окружения."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)


class RequestApiError(Exception):
    """Ошибка при попытке запроса к API."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)


class ApiAnswerStatusCodeError(Exception):
    """Статус-код ответа от API не соответствует ожидаемому."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)


class ApiResponseTypeError(TypeError):
    """API вернул не ожидаемый тип данных."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)


class ApiResponseAndParseKeyError(KeyError):
    """API вернул не ожидаемый набор ключей."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)


class WaitedHomeWorkVerdictError(ValueError):
    """Был получен вердикт которого нет в списке ожидаемых."""

    def __init__(self, message):
        """Добавление подробной информации об ошибке."""
        super().__init__(message)
