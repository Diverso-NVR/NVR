FROM python:3.7.7

WORKDIR /backend

COPY . /backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 5001
EXPOSE 5002

CMD [ "uwsgi", "--ini", "nvr.ini" ]