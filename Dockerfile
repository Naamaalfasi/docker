FROM python:3.10.13-slim

RUN apt-get update && apt-get install -y curl bash procps
WORKDIR /app

COPY requirements.txt .
COPY ./app/ .

RUN pip install --upgrade pip==23.3.1 && pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "main.py"]
