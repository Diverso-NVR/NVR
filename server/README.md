# backend
> nvr server side

## api:
``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requierments.txt
python3 appserver.py
``` 

## database:
``` bash
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
``` 

### if not up-to-date error occurred:
``` bash
python3 manage.py db stamp heads
```
