FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

EXPOSE 5000

CMD ["python", "web_app.py"]