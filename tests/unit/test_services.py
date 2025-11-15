import pytest
from app.services import security
from app.services import task_service
from app.schemas.task import TaskCreate

# Fixture for password testing
@pytest.fixture
def test_password():
    return "strong-password!123"

def test_password_hashing(test_password):
    """
    Tests that password hashing and verification work.
    """
    hashed_password = security.get_password_hash(test_password)
    assert hashed_password != test_password
    assert security.verify_password(test_password, hashed_password)
    assert not security.verify_password("wrong-password", hashed_password)

def test_task_service_custom_filter(db_session, test_user):
    """
    Unit test for the custom SQL query  in the task service.
    This fulfills the 'unit test for a business-logic function' requirement.
    """
    # 1. Create test data
    task_service.create_task(
        db_session, 
        TaskCreate(title="Find Python bug", description="A bug in the code"), 
        test_user.id
    )
    task_service.create_task(
        db_session, 
        TaskCreate(title="Write report", description="A report on Python"), 
        test_user.id
    )
    task_service.create_task(
        db_session, 
        TaskCreate(title="Do laundry", description="Weekly chore"), 
        test_user.id
    )

    # 2. Test filter for "Python"
    total, tasks = task_service.get_all_tasks(
        db_session, 
        owner_id=test_user.id,
        filter_query="Python"
    )
    
    assert total == 2
    assert len(tasks) == 2
    assert tasks[0].title == "Find Python bug"
    assert tasks[1].title == "Write report"

    # 3. Test filter for "chore"
    total, tasks = task_service.get_all_tasks(
        db_session, 
        owner_id=test_user.id,
        filter_query="chore"
    )
    
    assert total == 1
    assert len(tasks) == 1
    assert tasks[0].title == "Do laundry"