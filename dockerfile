FROM alpine

WORKDIR /app

RUN apk add python3 && apk add --update py3-pip &&\
    python3 -m pip install pipenv
ARG LANG=python3
COPY Pipfile* /app/
RUN pipenv sync

COPY . /app
CMD python manage.py runserver
