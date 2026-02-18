# HelpDesk DevOps

Sistema de gerenciamento de chamados para equipes de DevOps, construído com Django e TailwindCSS.

## Tecnologias

- **Python 3.12+**
- **Django 5.1.6**
- **SQLite**
- **TailwindCSS 3.4** (standalone CLI)

## Rodando Localmente

### 1. Clone o repositório

```bash
git clone <url-do-repo>
cd helpdesk-devops
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Aplique as migrations

```bash
python manage.py migrate
```

### 4. Crie um superusuário (ADMIN)

```bash
python manage.py createsuperuser
```

> Informe e-mail, nome, sobrenome e senha. O superusuário é criado automaticamente com role `ADMIN`.

### 5. Baixe o TailwindCSS standalone e compile o CSS

```bash
# macOS ARM
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss

# Compilar CSS
./tailwindcss -i static/css/input.css -o static/css/output.css --minify
```

> Para desenvolvimento com rebuild automático, use `--watch` no lugar de `--minify`.

### 6. Inicie o servidor

```bash
python manage.py runserver
```

Acesse [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)

## Scripts Úteis

| Script | Descrição |
|---|---|
| `./scripts/fix_templates.sh` | Valida se os templates HTML estão em uma única linha |
| `./scripts/fix_templates.sh --fix` | Corrige templates com quebras de linha |

## Estrutura do Projeto

```
helpdesk-devops/
├── helpdesk/            # Configuração do projeto Django
├── app_accounts/        # Autenticação e modelo de usuário
├── app_teams/           # Gestão de times (N1/N2)
├── app_tickets/         # Chamados, comentários e auditoria
├── templates/           # Templates HTML (single-line)
│   ├── components/      # Componentes reutilizáveis
│   ├── accounts/        # Login, perfil
│   └── teams/           # Listagem e detalhe de times
├── static/css/          # TailwindCSS (input/output)
└── scripts/             # Scripts utilitários
```
