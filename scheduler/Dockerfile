FROM python:3.8-slim-buster

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN useradd -U -s /bin/false app
USER app

COPY shared /app/shared
COPY scheduler /app/scheduler

EXPOSE 8102

CMD ["uvicorn", "scheduler.main:app", "--host", "0.0.0.0", "--port", "8102"]
