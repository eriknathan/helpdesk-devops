#!/bin/bash
set -e

echo "Aguardando o PostgreSQL..."
while ! python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('${DB_HOST:-db}', ${DB_PORT:-5432}))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
    echo "PostgreSQL indisponível - aguardando..."
    sleep 1
done

echo "PostgreSQL disponível!"

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Iniciando servidor..."
exec gunicorn helpdesk.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
