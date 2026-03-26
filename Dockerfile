FROM    python:3.13-slim

ENV     PYTHONUNBUFFERED=1
ENV     PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN     apt-get update && apt-get install git -y

COPY    ["requirements.txt", "."]

RUN     pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY    ["src", "."]

RUN     useradd -m nonroot
USER    nonroot

CMD     ["python", "main.py"]
