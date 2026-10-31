FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# The application resolves frontend and database paths from the repository root.
WORKDIR /app
COPY backend/app /app/backend/app
COPY frontend/pages /app/frontend/pages
COPY frontend/public /app/frontend/public
COPY database/schema.sql /app/database/schema.sql
COPY database/seed_data.sql /app/database/seed_data.sql
COPY scripts/migrate_sqlite_to_mysql.py /app/scripts/migrate_sqlite_to_mysql.py

WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
