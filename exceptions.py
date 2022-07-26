class StatusCodeError(Exception):
    """Код запроса отличается от 200."""
    pass


class StatusError(Exception):
    """Статус домашки с ошибочным значением."""
    pass


class APIResponseException(Exception):
    """Исключение для проверки ответа API на корректность."""
    pass


class RequestExceptionError(Exception):
    """Ошибка запроса."""
