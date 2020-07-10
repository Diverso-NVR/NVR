FROM python:3.7.7

WORKDIR /backend

COPY . /backend
COPY ./creds /root/creds

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "uwsgi", "--ini", "nvr.ini" ]