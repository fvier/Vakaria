FROM python:3.13-slim

# Evita que o Python gere arquivos .pyc e força stdout imediato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instala dependências de compilação essenciais e libpq
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código do projeto
COPY . .

# Expõe a porta do Django
EXPOSE 8000

# Script de inicialização que roda migrações, coleta estáticos e inicia Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 60 --access-logfile - --error-logfile -"]
