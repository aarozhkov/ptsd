FROM python:3.8-slim-buster

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN useradd -U -s /bin/false app
USER app

COPY shared /app/
COPY status /app/

EXPOSE 8101

CMD ["uvicorn", "status.main:app", "--port", "8101"]
