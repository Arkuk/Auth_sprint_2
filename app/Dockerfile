FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./src/requirements.txt .

RUN apt update -y  \
    && apt install netcat -y \
    && pip install --upgrade pip  \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["sh","./src/docker-entrypoint.sh"]