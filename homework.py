import logging
import os
import requests
import telegram
import time

from http import HTTPStatus
from dotenv import load_dotenv

from exceptions import APIResponseException, StatusCodeError, StatusError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


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
    except ConnectionError:
        message = 'Ошибка подключения к API.'
        logger.error(message)
        raise ConnectionError(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Эндпоинт API не доступен. Статус: {response.status_code}.'
        logger.error(message)
        raise StatusCodeError(message)
    logger.info('Запрос к эндпоинту успешно выполнен.')
    return response.json()


def check_response(response):
    """Проверка корректности ответа API."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        message = 'В словаре нет ключа homeworks.'
        logger.error(message)
        raise KeyError(message)
    if len(homeworks) == 0:
        message = 'На проверку ничего не отправлено.'
        logger.error(message)
        raise APIResponseException(message)
    if not isinstance(homeworks, list):
        message = 'В ответе API домашки выводятся не списком.'
        logger.error(message)
        raise APIResponseException(message)
    logger.info('Полученные данные корректны.')
    return homeworks


def parse_status(homework):
    """Проверка обновления статуса работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_name is None:
        message = 'В словаре нет ключа homework_name .'
        logger.error(message)
        raise KeyError(message)
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
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, START_MESSAGE)
    hw_status = ''
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework and hw_status != homework['status']:
                message = parse_status(homework)
                send_message(bot, message)
                hw_status = homework['status']
            else:
                message = 'Изменений нет, ждем 10 минут и проверяем API'
                send_message(bot, message)
                logger.info(message)
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
