FROM python:3.10-alpine3.17

WORKDIR /enrollment
COPY . .
COPY docker.env_example .env
RUN pip install -r requirements.txt

ENV POSTGRES_SERVER=db
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV DATABASE_HOST=db
ENV DATABASE_USERNAME=postgres
ENV DATABASE_PASSWORD=password
ENV DATABASE_DB_NAME=postgres

EXPOSE 8080

RUN apk update && apk add postgresql-client
CMD until nc -z ${POSTGRES_SERVER} ${POSTGRES_PORT}; do echo "Waiting for Postgres..." && sleep 1; done \
    && psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB} --list; alembic upgrade head; uvicorn app.main:app --host=0.0.0.0 --port=8080