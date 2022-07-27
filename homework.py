import json
import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    APIResponseException, RequestExceptionError, StatusCodeError, StatusError
)


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


START_MESSAGE = 'Привет! Я готов тебе помочь!'


logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Сообщение в Telegram отправлено: {message}')
    except telegram.TelegramErrors as telegram_error:
        message = f'Сообщение в Telegram не отправлено: {telegram_error}'
        logger.error(message)


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
        if response.status_code != HTTPStatus.OK:
            message = f'Эндпоинт API не доступен: {response.status_code}.'
            logger.error(message)
            raise StatusCodeError(message)
        logger.info('Запрос к эндпоинту успешно выполнен.')
        return response.json()
    except requests.exceptions.RequestException:
        message = 'Ошибка подключения к API.'
        logger.error(message)
        raise RequestExceptionError(message)
    except json.JSONDecodeError as error:
        message = f'Код ответа API: {error}'
        logger.error(message)
        raise json.JSONDecodeError(message)


def check_response(response):
    """Проверка корректности ответа API."""
    if not isinstance(response, dict):
        message = 'Неправильный тип полученного ответа'
        logging.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В словаре нет ключа homeworks .'
        logger.error(message)
        raise KeyError(message)
    homeworks_list = response['homeworks']
    if not isinstance(homeworks_list, list):
        message = 'В ответе API домашки выводятся не списком.'
        logger.error(message)
        raise APIResponseException(message)
    logger.info('Полученные данные корректны.')
    return homeworks_list


def parse_status(homework):
    """Проверка обновления статуса работы."""
    if not (('homework_name' in homework) and ('status' in homework)):
        message = 'Отсутствуют имя и статус домашней работы'
        logging.error(message)
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_name is None:
        message = 'Пустое значение.'
        logger.error(message)
        raise StatusError(message)
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Статус домашки с недокументированным значением.'
        logger.error(message)
        raise StatusError(message)
    verdict = HOMEWORK_STATUSES[homework_status]
    logger.info('Обновлен статус проверки работы.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    token_status = True
    check_params = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    for value in check_params:
        if value is None:
            token_status = False
            message = f'Программа остановлена. Отсутствует: {value}.'
            logger.critical(message)
            return token_status
    logger.info('Получен доступ к необходимым переменным окружения.')
    return token_status


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        exit()
    send_message(bot, START_MESSAGE)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            try:
                homework = check_response(response)[0]
                message = parse_status(homework)
            except IndexError:
                message = 'Список пуст'
            send_message(bot, message)
            current_timestamp = response.get('current_date', current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
