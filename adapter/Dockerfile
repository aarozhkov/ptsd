FROM python:3.8-slim-buster

WORKDIR /app/

COPY requirements.txt .

RUN useradd -U -s /bin/false app
RUN pip install -r requirements.txt --no-cache-dir

USER app

COPY shared /app/shared
COPY adapter /app/adapter

CMD ["uvicorn", "adapter.main:adapter_api", "--port", "8000"]
