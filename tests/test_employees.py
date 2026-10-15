
from datetime import date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.employees import (
    validate_employee_dates,
    validate_hire_date_range,
)


client = TestClient(app)


def test_list_employees():
    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert data["count"] >= 0


def test_list_employees_with_pagination():
    response = client.get(
        "/api/v1/employees",
        params={"limit": 5, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert len(data["employees"]) <= 5


def test_search_employees():
    response = client.get(
        "/api/v1/employees",
        params={"q": "EMP-0001"},
    )

    assert response.status_code == 200
    assert any(
        employee["employee_id"] == "EMP-0001"
        for employee in response.json()["employees"]
    )


def test_filter_employees_by_department():
    employee_response = client.get("/api/v1/employees/EMP-0001")
    assert employee_response.status_code == 200

    department_id = employee_response.json().get("department_id")
    if department_id is None:
        pytest.skip("EMP-0001 has no department assigned.")

    response = client.get(
        "/api/v1/employees",
        params={"department_id": department_id},
    )

    assert response.status_code == 200
    assert all(
        employee["department_id"] == department_id
        for employee in response.json()["employees"]
    )


def test_invalid_hire_date_range():
    response = client.get(
        "/api/v1/employees",
        params={
            "hire_date_from": "2026-12-31",
            "hire_date_to": "2026-01-01",
        },
    )

    assert response.status_code == 422


def test_get_existing_employee():
    response = client.get("/api/v1/employees/EMP-0001")

    assert response.status_code == 200
    assert response.json()["employee_id"] == "EMP-0001"


def test_get_missing_employee():
    response = client.get(
        "/api/v1/employees/EMP-DOES-NOT-EXIST"
    )

    assert response.status_code == 404


def test_create_update_and_soft_delete_employee():
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

        update_response = client.put(
            f"/api/v1/employees/{employee_id}",
            json={"full_name": "Automated Tester Updated"},
        )
        assert update_response.status_code == 200
        assert (
            update_response.json()["full_name"]
            == "Automated Tester Updated"
        )

        delete_response = client.delete(
            f"/api/v1/employees/{employee_id}"
        )
        assert delete_response.status_code == 200

        inactive_response = client.get(
            f"/api/v1/employees/{employee_id}"
        )
        assert inactive_response.status_code == 404

    finally:
        # Preserve soft-delete semantics; never physically delete the row.
        # If an assertion fails before deletion, attempt normal soft deletion.
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


def test_create_employee_with_future_hire_date_is_rejected():
    payload = {
        "employee_id": "EMP-AUTO-FUTURE-903",
        "first_name": "Future",
        "last_name": "Hire",
        "full_name": "Future Hire",
        "work_email": "future.hire.903@example.com",
        "employment_status": "Active",
        "hire_date": "2026-10-01",
    }

    response = client.post("/api/v1/employees", json=payload)

    assert response.status_code == 422


def test_create_employee_with_blank_name_is_rejected():
    payload = {
        "employee_id": "EMP-AUTO-BLANK-904",
        "first_name": " ",
        "last_name": "Tester",
        "full_name": "Blank Tester",
        "work_email": "blank.name.904@example.com",
        "employment_status": "Active",
    }

    response = client.post("/api/v1/employees", json=payload)

    assert response.status_code == 422


def test_valid_employee_dates():
    validate_employee_dates(
        date(2026, 9, 30),
        date(2026, 9, 30),
    )


def test_future_hire_date_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        validate_employee_dates(date(2026, 10, 1), None)

    assert exc_info.value.status_code == 422


def test_exit_date_before_hire_date_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        validate_employee_dates(
            date(2026, 9, 30),
            date(2026, 9, 29),
        )

    assert exc_info.value.status_code == 422


def test_valid_hire_date_range():
    validate_hire_date_range(
        date(2026, 1, 1),
        date(2026, 9, 30),
    )


def test_reversed_hire_date_range_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        validate_hire_date_range(
            date(2026, 9, 30),
            date(2026, 1, 1),
        )

    assert exc_info.value.status_code == 422
