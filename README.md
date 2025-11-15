# FastAPI Task CRUD Service

This is a professional-grade FastAPI application demonstrating CRUD operations for a "Task" resource. It is built following best practices, including a clean architecture, SOLID principles, testing, and Docker support.

## Features

* **FastAPI**: High-performance web framework.
* **SQLAlchemy**: ORM for database interaction.
* **Pydantic**: Data validation for requests and responses.
* **Alembic**: Database migrations.
* **PostgreSQL**: Relational database.
* **JWT Authentication**: Secure endpoints.
* **Docker**: Full containerization with Docker Compose.
* **Pagination & Sorting**: Implemented for list endpoints.
* **Clean Architecture**: Service layer, repository pattern (implicit), and modular code.
* **Testing**: Unit and integration tests with `pytest`.

## Project Setup & Running

### 1. Prerequisites

* Python 3.10+
* Docker & Docker Compose

### 2. Local Setup (without Docker)

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd fastapi-task-project
   ```
2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Copy the example file:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your database credentials and a JWT secret.
5. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```
6. **Run the application:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.
   Swagger Docs: `http://127.0.0.1:8000/docs`

### 3. Docker Setup (Recommended)

1. **Clone the repository.**
2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` to your preferences. The `docker-compose.yml` is configured to use these values.
3. **Build and run the containers:**

   ```bash
   docker-compose up -d --build
   ```

   This command will:

   * Build the `fastapi_app` service.
   * Start the `db` (PostgreSQL) service.
   * Run the database migrations automatically via the `entrypoint.sh` script.
   * Start the FastAPI application.

   The API will be available at `http://127.0.0.1:8000`.

### 4. Running Tests

To run the test suite:

```bash
pytest
```
