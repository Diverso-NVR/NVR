FROM node:latest as build-front

ARG NVR_CLIENT_URL

WORKDIR /frontend

COPY frontend/package.json /frontend
COPY frontend/package-lock.json /frontend

RUN npm install

COPY frontend /frontend

RUN npm run build

FROM python:3.7

WORKDIR /backend

COPY --from=build-front /frontend/dist /dist

COPY backend /backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "uwsgi", "--ini", "nvr.ini"]
