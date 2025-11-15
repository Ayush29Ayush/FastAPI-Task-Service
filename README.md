# FastAPI Task CRUD Service

This is a professional-grade FastAPI application demonstrating CRUD operations for a "Task" resource. It is built following best practices, including a clean architecture, SOLID principles, testing, and Docker support.

## Features

* **FastAPI**: High-performance web framework.
* **SQLAlchemy**: ORM for database interaction.
* **Pydantic**: Data validation for requests and responses.
* **Alembic**: Database migrations.
* **PostgreSQL**: Relational database (via Docker).
* **JWT Authentication**: Secure endpoints.
* **Docker**: Full containerization with Docker Compose.
* **Pagination & Sorting**: Implemented for list endpoints.
* **Clean Architecture**: Service layer, repository pattern (implicit), and modular code.
* **Testing**: Unit and integration tests with `pytest`.

## Project Setup & Running (Docker)

This project is designed to be run with Docker and Docker Compose. This is the recommended and supported method.

### 1. Prerequisites

* Python 3.10+ (for `venv` if desired, though not required)
* Docker & Docker Compose

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd fastapi-task-project
```

### 3. Set Up Environment Variables

You must create a `.env` file in the project root.

1.  Copy the example file:
    ```bash
    cp .env.example .env
    ```

2.  Open the new `.env` file and ensure it contains the following. **You must change `SECRET_KEY` to a strong, unique string.**

    ```ini
    # Application
    PROJECT_NAME="FastAPI Task Service"
    API_V1_STR="/api/v1"
    
    # Database (PostgreSQL) - Used by Docker Compose
    DATABASE_URL="postgresql://user:password@db:5432/appdb"
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=appdb
    
    # Test Database - Used by Pytest
    TEST_DATABASE_URL="postgresql://user:password@test_db:5432/appdb_test"
    POSTGRES_TEST_DB=appdb_test
    
    # JWT Authentication
    SECRET_KEY="replace-this-with-a-very-long-and-random-string"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

### 4. Build and Run the Containers

```bash
docker-compose up -d --build
```

This command will:
* Build the `fastapi_app` service from the `Dockerfile`.
* Start the `db` (PostgreSQL) service for the application.
* Start the `test_db` (PostgreSQL) service for testing.
* Run database migrations automatically via the `entrypoint.sh` script.
* Start the FastAPI application.

The API will be available at `http://127.0.0.1:8000`.
* **Interactive Docs (Swagger):** `http://127.0.0.1:8000/docs`
* **Health Check:** `http://127.0.0.1:8000/health`

---

## Running the Test Suite

To run the full `pytest` suite against the **test database**, use the following command.

```bash
docker-compose exec app env ENV_STATE=test pytest
```

**Why this command?**
* `docker-compose exec app`: Runs a command inside the running `app` container.
* `env ENV_STATE=test`: This is **critical**. It sets the environment variable that tells our app to use the `TEST_DATABASE_URL` (connecting to `appdb_test`) instead of the main `appdb`.
* `pytest`: Runs the test suite.

---

## API Walkthrough (via `curl`)

Here is a quick walkthrough to test all functionality from your terminal.

### 1. Authentication

First, create a user and get an access token.

**Step 1: Create a User**
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
```
*Response: `{"email":"user@example.com","id":1}`*

**Step 2: Log In**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=password123"
```
*Response: `{"access_token":"...your_token...","token_type":"bearer"}`*

**Step 3: Export Your Token**
Copy the `access_token` and store it in a shell variable for easy use.
```bash
export TOKEN="...paste_your_token_here..."
```

### 2. Task CRUD Operations

Now you can access the protected `/tasks` endpoints.

**Step 1: Create a Task**
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Task", "description": "Buy milk"}'
```
*Response: `{"title":"My First Task","description":"Buy milk","id":1,...}`*
(Note down the `id` you get, e.g., `1`)

**Step 2: Get All Tasks (with filtering/pagination)**
```bash
# Get all tasks
curl -X GET "http://localhost:8000/api/v1/tasks/" -H "Authorization: Bearer $TOKEN"

# Get tasks with "milk" in the title/description
curl -X GET "http://localhost:8000/api/v1/tasks/?filter=milk" -H "Authorization: Bearer $TOKEN"

# Get 1 task, skipping the first 0 (e.g., page 1)
curl -X GET "http://localhost:8000/api/v1/tasks/?limit=1&offset=0" -H "Authorization: Bearer $TOKEN"
```

**Step 3: Get a Single Task (use the `id` from Step 1)**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1" -H "Authorization: Bearer $TOKEN"
```

**Step 4: Update the Task**
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Updated Task Title"}'
```

**Step 5: Delete the Task**
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1" -H "Authorization: Bearer $TOKEN"
```
*Response: (No content, status code 204)*