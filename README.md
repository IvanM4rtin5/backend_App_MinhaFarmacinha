# Minha Farmacinha - Backend - in developing

Backend da aplicação Minha Farmacinha, desenvolvido com FastAPI.

## Requisitos

- Python 3.8+
- PostgreSQL
- Firebase (para autenticação)

## Configuração do Ambiente

1. Clone o repositório
2. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Copie o arquivo `.env.example` para `.env` e configure as variáveis de ambiente:

```bash
cp .env.example .env
```

5. Configure o banco de dados:

```bash
alembic upgrade head
```

6. Execute a aplicação:

```bash
uvicorn app.main:app --reload
```

## Estrutura do Projeto

```
app/
├── api/          # Rotas da API
├── core/         # Configurações core
├── models/       # Modelos SQLAlchemy
├── schemas/      # Schemas Pydantic
├── services/     # Lógica de negócio
└── utils/        # Utilitários
```

## Documentação da API

A documentação da API estará disponível em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testes

Para executar os testes:

```bash
pytest
```
