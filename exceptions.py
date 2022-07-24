class StatusCodeError(Exception):
    """Код запроса отличается от 200."""
    pass


class StatusHomeWorkError(Exception):
    """Статус домашки с ошибочным значением."""
    pass


class APIResponseException(Exception):
    """Исключение для проверки ответа API на корректность."""
    pass