# NVR Backend

## Запуск dev

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 appserver.py
```

## Структура

- **core/** - основная папка со всем функционалом:

  - **apis/** - папка скриптов API внешних сервисов 
  - **routes/** - папка NVR API по группам
  - **application.py** - создание приложения
  - **config.py** - класс переменных конфигурации
  - **decorators.py** - декораторы для работы
  - **email.py** - функции для email оповещений
  - **models.py** - модели бд
  - **socketio.py** - методы приложения для взаимодействия с клиентской частью по сокетам

- **logs/** - папка логов

- **migrations/** - папка данных sqlalchemy: версии миграции бд и т.п.

- **templates/email/** - шаблоны email сообщений

- **appserver.py** - скрипт запуска dev

- **manage.py** - скрипт управления бд через python-интерпретатор

- **nvr.ini** - файл конфигурации uwsgi сервера

- **requirements.txt** - список Python-библиотек, необходимых для работы
  приложения. Получается при помощи команды `pip freeze > requirements.txt`.
  Библиотеки устанавливаются в окружение при помощи команды
  `pip install -r requirements.txt`.

- **wsgi.py** - скрипт запуска prod
