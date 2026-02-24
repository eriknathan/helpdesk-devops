.PHONY: build up down restart logs shell migrate createsuperuser collectstatic clean

# Buildar as imagens
build:
	docker compose build

# Subir os containers
up:
	python3 scripts/format_templates.py --fix
	docker compose up -d --build

# Subir com logs visíveis
up-logs:
	docker compose up --build

# Parar os containers
down:
	docker compose down

# Parar e remover volumes (apaga dados do banco!)
down-clean:
	docker compose down -v

# Reiniciar os containers
restart:
	docker compose down
	docker compose up -d --build

# Ver logs
logs:
	docker compose logs -f

# Logs apenas do app
logs-web:
	docker compose logs -f web

# Logs apenas do banco
logs-db:
	docker compose logs -f db

# Shell interativo no container do app
shell:
	docker compose exec web python manage.py shell

# Bash no container do app
bash:
	docker compose exec web bash

# Rodar migrações
migrate:
	docker compose exec web python manage.py migrate

# Criar migrações
makemigrations:
	docker compose exec web python manage.py makemigrations

# Criar superusuário
superuser:
	docker compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

# Status dos containers
status:
	docker compose ps

# Limpar imagens, containers e volumes órfãos
clean:
	docker compose down -v --rmi local --remove-orphans
