FROM python:3.8-slim-buster

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apt update && apt install -y --no-install-recommends openjdk-11-jre-headless && apt autoremove
RUN useradd -U -s /bin/false app
USER app

COPY shared /app/
COPY supervisor /app/
COPY adapter /app/

EXPOSE 8112-8113

CMD ["python3", "-m" "supervisor.main"]