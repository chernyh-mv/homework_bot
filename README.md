## Homework_bot - проект в рамках курса от Яндекс Практикума
---
**У бота есть следующие задачи:**
 - раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
 - при обновлении статуса анализировать ответ API и отправлять пользователю соответствующее уведомление в Telegram;
 - логировать свою работу и сообщать пользователю о важных проблемах сообщением в Telegram.
 
**Для его создания использовались следующие технологии:**

*Python 3, Django, Django REST Framework, Simple-JWT*

**Как запустить проект:**
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:chernyh-mv/homework_bot.git
```

```
cd homework_bot/
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Создаем .env файл с токенами:

```
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
```

Запускаем бота:

```
python homework.py
```
___
___
*Автор: [Мария Черных](https://github.com/chernyh-mv)*