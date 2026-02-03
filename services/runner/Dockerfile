FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY packages/core /app/packages/core
COPY services/runner /app/services/runner

RUN python -m pip install --upgrade pip \
    && python -m pip install -e /app/packages/core \
    && python -m pip install -e /app/services/runner

WORKDIR /app/services/runner

CMD ["uvicorn", "runner.api:app", "--host", "0.0.0.0", "--port", "9002"]
