FROM node:latest

ARG NVR_CLIENT_URL

WORKDIR /frontend

COPY package.json /frontend
COPY package-lock.json /frontend

RUN npm install

COPY . /frontend

RUN npm run build

ENTRYPOINT "cp -RT /frontend/dist /tmp/dist; sleep infinity"
