# NVR backend

## Запуск dev:
``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 appserver.py
``` 

## Структура 

* **.creds/** - папка данных авторизация для Google API

* **driveAPI/driveSettings.py** - содержит  функции для взаимодействия с Google Drive API.

* **calendarAPI/calendarSettings.py** - содержит функции для взаимодействия с Google Calendar API.

* **logs/** - папка логов

* **migrations/** - папка данных sqlalchemy: версии миграции бд и т.п.

* **nvrAPI/** - основная папка со всем функционалом:
    * **api.py** - все методы API NVR
    * **application.py** - создание приложения
    * **config.py** - класс переменных конфигурации
    * **email.py** - функции для email оповещений
    * **models.py** - модели бд
    * **socketio.py** - методы приложения для взаимодействия с клиентской частью по сокетам

* **templates/email/** - шаблоны email сообщений

* **appserver.py** - скрипт запуска dev

* **manage.py** - скрипт управления бд через python-интерпретатор

* **nvr.ini** - файл конфигурации uwsgi сервера

* **requirements.txt** - список Python-библиотек, необходимых для работы 
приложения. Получается при помощи команды `pip freeze > requirements.txt`. 
Библиотеки устанавливаются в окружение при помощи команды 
`pip install -r requirements.txt`. 

* **wsgi.py** - скрипт запуска prod