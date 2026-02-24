FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema para psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Copiar e dar permissão ao entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
