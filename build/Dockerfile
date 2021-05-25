FROM node:12.18.4 as build-front

ARG NVR_CLIENT_URL

WORKDIR /frontend

COPY frontend/package.json /frontend

RUN npm install

COPY frontend /frontend

RUN npm run build

FROM python:3.7

WORKDIR /backend

COPY --from=build-front /frontend/dist /dist

COPY backend /backend

RUN apt-get install apt-transport-https ca-certificates curl gnupg lsb-release
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
RUN echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install docker-ce docker-ce-cli containerd.io

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "uwsgi", "--ini", "nvr.ini"]
