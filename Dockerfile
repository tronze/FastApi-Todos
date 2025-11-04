# <django_project>/Dockerfile-dev
FROM python:3.11

RUN mkdir /code

WORKDIR /code

COPY ./src /code

COPY ./requirements-prod.txt /code

RUN pip3 install --no-cache-dir -r /code/requirements-prod.txt

CMD ["fastapi", "run", "main.py", "--port", "8000"]