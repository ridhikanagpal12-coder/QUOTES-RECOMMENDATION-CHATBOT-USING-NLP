FROM rasa/rasa:3.6.2

WORKDIR /app

COPY . /app

CMD ["run","--enable-api","--cors","*","--port","10000","--model","models"]