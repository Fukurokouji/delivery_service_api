FROM python:3.10-alpine3.17 as apply_migrations
COPY . .
RUN pip install -r requirements.txt
RUN apk update && apk add postgresql
ENV POSTGRES_SERVER=db
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV DATABASE_HOST=db
ENV DATABASE_USERNAME=postgres
ENV DATABASE_PASSWORD=password
ENV DATABASE_DB_NAME=postgres
CMD alembic upgrade head

FROM python:3.10-alpine3.17 as main_app
COPY . .
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
CMD uvicorn app.main:app --host=0.0.0.0 --port=8080