# A tiny HTTP API that reports whether it can reach its database.
# GET /up answers 200 when PostgreSQL answers, 503 when it does not; bin/report prints a one-line report.
FROM python:3.13-slim-trixie@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

RUN pip install --no-cache-dir "psycopg[binary]==3.3.9"

WORKDIR /app
COPY app.py ./
COPY bin/report ./bin/report
USER nobody
EXPOSE 8080
CMD ["python", "app.py"]
