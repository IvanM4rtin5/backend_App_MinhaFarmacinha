# Minha Farmacinha - Backend - in development

Backend of the Minha Farmacinha application, developed with FastAPI.

## Requirements

- Python 3.8+
- PostgreSQL
- Firebase (for authentication)

## Environment Configuration

1. Clone the repository
2. Create a virtual environment:

```bash
python -m venv venv
```
And activate the venv
```bash
source venv/bin/activate # Linux/Mac
.\venv\Scripts\activate # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the `.env.example` file to `.env` and configure the environment variables:

```bash
cp .env.example .env
```
5. Configure the database:
```bash
alembic upgrade head
```
6. Run the application:
```bash
uvicorn app.main:app --reload
```
## Project Structure

```
app/
├── api/ # API Routes
├── core/ # Core Settings
├── models/ # SQLAlchemy Models
├── schemas/ # Schemas Pydantic
├── services/ # Business logic
└── utils/ # Utilities
```

## API documentation

API documentation will be available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tests

To run the tests:

```bash
pytest
```
