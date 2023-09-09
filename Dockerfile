
FROM python:3.11.2

ENV APP_HOME /APP_HOME

WORKDIR ${APP_HOME}

COPY . .

RUN pip install -r requirements.txt

EXPOSE 4000

ENTRYPOINT ["python3", "main.py"]