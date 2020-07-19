FROM node:latest as build

ARG NVR_CLIENT_URL

WORKDIR /frontend

COPY package.json /frontend
COPY package-lock.json /frontend

RUN npm install

COPY . /frontend

RUN npm run build


FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY --from=build /frontend/dist /usr/share/nginx/html
COPY nginx/proxy_params /etc/nginx/
COPY nginx/uwsgi_params /etc/nginx/
COPY nginx/nginx.conf /etc/nginx/conf.d/

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]
