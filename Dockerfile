FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HOST="localhost" USER="user" PASS="pass"

CMD ["sh", "-c", "python main.py"]
