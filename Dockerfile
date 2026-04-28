FROM python:3.12-slim

# Evita arquivos .pyc e buffer
ENV PYTHONDONTWRITEBYTECODE=1
# ✅ BUG CORRIGIDO: era PYTHONNUNBUFFERED (com N duplo)
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["python", "main.py"]
