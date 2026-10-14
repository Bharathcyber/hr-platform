
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_employees():
    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert data["count"] >= 0


def test_get_existing_employee():
    response = client.get("/api/v1/employees/EMP-0001")

    assert response.status_code == 200
    assert response.json()["employee_id"] == "EMP-0001"


def test_get_missing_employee():
    response = client.get("/api/v1/employees/EMP-DOES-NOT-EXIST")

    assert response.status_code == 404


def test_create_and_delete_employee():
    payload = {
        "employee_id": "EMP-AUTO-TEST-901",
        "first_name": "Automated",
        "last_name": "Tester",
        "full_name": "Automated Tester",
        "work_email": "automated.tester.901@znova-demo.example",
        "employment_status": "Active",
    }

    create_response = client.post(
        "/api/v1/employees",
        json=payload,
    )

    assert create_response.status_code == 201

    employee_id = payload["employee_id"]

    try:
        get_response = client.get(
            f"/api/v1/employees/{employee_id}"
        )
        assert get_response.status_code == 200

    finally:
        client.delete(f"/api/v1/employees/{employee_id}")


def test_duplicate_employee_id():
    payload = {
        "employee_id": "EMP-0001",
        "first_name": "Duplicate",
        "last_name": "Tester",
        "full_name": "Duplicate Tester",
        "work_email": "unique.duplicate.tester@znova-demo.example",
        "employment_status": "Active",
    }

    response = client.post(
        "/api/v1/employees",
        json=payload,
    )

    assert response.status_code == 409


def test_invalid_email():
    payload = {
        "employee_id": "EMP-AUTO-TEST-902",
        "first_name": "Invalid",
        "last_name": "Email",
        "full_name": "Invalid Email",
        "work_email": "not-an-email",
        "employment_status": "Active",
    }

    response = client.post(
        "/api/v1/employees",
        json=payload,
    )

    assert response.status_code == 422
