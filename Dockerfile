FROM  python:3.10-slim

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD [ "python", "main.py" ]