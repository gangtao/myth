FROM python:slim
WORKDIR /app
ADD ./requirements.txt /app
ADD ./src /app

RUN pip install -r requirements.txt

CMD pytest 