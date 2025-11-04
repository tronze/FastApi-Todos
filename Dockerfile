# <django_project>/Dockerfile-dev
FROM python:3.11-slim

RUN addgroup --system app && adduser --system --ingroup app --uid 10001 app

RUN mkdir /code

WORKDIR /code

COPY ./src /code

COPY ./requirements-prod.txt /code

RUN pip3 install --no-cache-dir -r /code/requirements-prod.txt

COPY --chown=app:app . .

USER app

CMD ["fastapi", "run", "main.py", "--port", "8000"]