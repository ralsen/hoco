FROM python:3.11-slim

WORKDIR /app

# Falls du eine requirements.txt hast:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "hoco.py"]
