FROM python:3.7.7

WORKDIR /backend

COPY . /backend

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "uwsgi", "nvr.ini" ]