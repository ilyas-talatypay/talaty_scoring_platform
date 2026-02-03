FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY packages/core /app/packages/core
COPY services/api /app/services/api

RUN python -m pip install --upgrade pip \
    && python -m pip install -e /app/packages/core \
    && python -m pip install -e /app/services/api

WORKDIR /app/services/api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
