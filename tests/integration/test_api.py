from fastapi.testclient import TestClient
from app.core.config import settings

def test_health_check(client: TestClient):
    """
    Tests the /health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_user(client: TestClient):
    """
    Tests user creation endpoint.
    """
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        json={"email": "newuser@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_create_duplicate_user(client: TestClient, test_user):
    """
    Tests that creating a user with a duplicate email fails.
    """
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        json={"email": test_user.email, "password": "password123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login(client: TestClient, test_user):
    """
    Tests the login endpoint.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    """
    Tests login with an incorrect password.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_task_crud_workflow(client: TestClient, auth_token_header: dict):
    """
    Tests the full CRUD workflow for tasks.
    This covers the 'integration test hitting at least one endpoint'.
    """
    task_id = None
    
    # 1. Create Task
    response = client.post(
        f"{settings.API_V1_STR}/tasks/",
        json={"title": "Test Task", "description": "Test Description"},
        headers=auth_token_header
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert "id" in data
    task_id = data["id"]

    # 2. Read Single Task
    response = client.get(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=auth_token_header
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

    # 3. Read All Tasks (List)
    response = client.get(
        f"{settings.API_V1_STR}/tasks/",
        headers=auth_token_header
    )
    assert response.status_code == 200
    list_data = response.json()
    assert list_data["total"] == 1
    assert len(list_data["data"]) == 1
    assert list_data["data"][0]["title"] == "Test Task"

    # 4. Update Task (PUT/PATCH)
    response = client.put(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        json={"title": "Updated Test Task"},
        headers=auth_token_header
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Task"
    assert response.json()["description"] == "Test Description" # Description was not updated

    # 5. Delete Task
    response = client.delete(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=auth_token_header
    )
    assert response.status_code == 204 # No Content

    # 6. Verify Deletion
    response = client.get(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=auth_token_header
    )
    assert response.status_code == 404 # Not Found