FROM python:3.8-slim-buster

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN useradd -U -s /bin/false app
USER app

EXPOSE 8080

CMD ["sleep", "1000"]