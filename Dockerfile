FROM node:alpine as build

WORKDIR /app

ENV VITE_API_URL http://localhost:5000/api

COPY frontend/package*.json ./

RUN npm install

COPY frontend/. ./

RUN npm run build

FROM python:alpine

LABEL maintainer="DmitryArkh <contact@dmitryarkh.me>"

WORKDIR /app

COPY --from=build /app/dist ./static

COPY backend/requirements.txt ./

RUN python -m pip install --no-cache-dir --upgrade --root-user-action ignore -r requirements.txt

RUN rm requirements.txt

COPY backend/. ./

EXPOSE 5000

ENTRYPOINT waitress-serve --host=0.0.0.0 --port=5000 --threads=6 main:app
