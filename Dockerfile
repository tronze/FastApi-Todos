# <django_project>/Dockerfile-dev
FROM python:3.11-slim

# Create non-root app user and base code dir
RUN addgroup --system app \
    && adduser --system --ingroup app --uid 10001 app \
    && mkdir -p /code

WORKDIR /code

# Copy source and requirements (keep them root-owned)
COPY ./src /code
COPY ./requirements-prod.txt /code/requirements-prod.txt

# Install dependencies
RUN pip3 install --no-cache-dir -r /code/requirements-prod.txt

# Harden: make copied code read-only for all (root-owned, no write), to satisfy Sonar rule
RUN chown -R root:root /code \
    && chmod -R a-w /code \
    && find /code -type d -exec chmod a+rx {} \; \
    && find /code -type f -exec chmod a+r {} \;

# Create writable data dir for the app user and point TODO_FILE there
RUN mkdir -p /data \
    && chown app:app /data \
    && chmod 0770 /data
ENV TODO_FILE=/data/todo.json

# Run as non-root
USER app

CMD ["fastapi", "run", "main.py", "--port", "8000"]