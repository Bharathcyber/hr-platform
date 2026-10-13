# HR Platform — API Contract

**Version:** 0.1.0  
**Status:** Draft for team integration

**Base URL:** `http://localhost:8000`

## 1. Health and service information

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| GET | `/` | API welcome message | Available |
| GET | `/health` | Backward-compatible health check | Available |
| GET | `/api/v1/health` | Versioned service and dependency health information | To be implemented and tested |

The versioned health endpoint should report the service name, application version, and health of configured dependencies. Dependency checks must reflect actual check results rather than assume that a dependency is healthy.

## 2. Employee and department endpoints

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| POST | `/employees` | Create an employee | Planned — Task 3 |
| GET | `/employees` | List, search, filter, and paginate employees | Planned — Task 3 |
| GET | `/employees/{id}` | Retrieve an employee | Planned — Task 3 |
| PATCH | `/employees/{id}` | Update an employee | Planned — Task 3 |
| DELETE | `/employees/{id}` | Deactivate an employee (soft delete) | Planned — Task 3 |
| GET | `/departments` | List departments | Planned — Task 3 |
| GET | `/departments/{id}/employees` | List employees in a department | Planned — Task 3 |
| GET | `/employees/{id}/team` | Retrieve direct reports | Planned — Task 3 |

## 3. API conventions

- Use JSON request and response bodies.
- Use appropriate HTTP status codes.
- Generate employee IDs on the server.
- Require unique employee work email addresses.
- Support pagination on list endpoints.
- Finalize the employee schema during Tasks 2 and 3.
- Document authentication and authorization requirements when those features are implemented.



## 4. Implementation notes

This document describes the intended API contract. Planned endpoints must not be treated as implemented until their corresponding functionality and tests are complete.

Database, Redis, and background-worker health checks must be integrated with the actual configured services before reporting them as healthy.