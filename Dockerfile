FROM python:3.8-slim-buster

WORKDIR /app/

RUN apt update && apt install -y --no-install-recommends openjdk-11-jre-headless curl \
    && curl -L https://github.com/allure-framework/allure2/releases/download/2.15.0/allure_2.15.0-1_all.deb -o /tmp/allure.deb \
    && dpkg -i /tmp/allure.deb \
    && rm -f /tmp/allure.deb \
    && chmod 777 /usr/bin/allure \
    && apt autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN useradd -U -s /bin/false app
RUN pip install -r requirements.txt --no-cache-dir

USER app

COPY . /app/


EXPOSE 8112-8113

CMD ["python3", "-m" "supervisor.main"]