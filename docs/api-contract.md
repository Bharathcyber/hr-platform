# HR Platform — API Contract

**Version:** 0.2.0
**Status:** Phase 1 implementation; authentication and remaining endpoints pending

**Base URL:** `http://localhost:8000`

## 1. Service and health endpoints

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/` | Implemented | API welcome message |
| GET | `/health` | Implemented | Backward-compatible health check |
| GET | `/api/v1/health` | Implemented | Versioned service and dependency health |

The versioned health endpoint reports the service name, version, overall status, and database, Redis, and worker checks. A dependency that is not configured must not be reported as healthy.

## 2. Employee endpoints

All employee routes use the `/api/v1/employees` prefix.

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/api/v1/employees` | Implemented | List employees with pagination and filters |
| GET | `/api/v1/employees/{employee_id}` | Implemented | Retrieve an employee |
| GET | `/api/v1/employees/team/{manager_id}` | Implemented | Retrieve a manager's direct reports |
| POST | `/api/v1/employees` | Implemented | Create an employee |
| PUT | `/api/v1/employees/{employee_id}` | Implemented | Update an employee |
| DELETE | `/api/v1/employees/{employee_id}` | Implemented | Deactivate an employee |

The list endpoint supports `limit`, `offset`, `department_id`, `role_id`, `employment_status`, `work_location`, `work_mode`, `manager_id`, hire-date range filters, and text search where implemented by the route.

The update endpoint requires at least one field. Employee creation returns HTTP 201. Duplicate employee IDs or work email addresses return HTTP 409. Invalid references can return HTTP 422. Deletion is intended to deactivate an employee rather than permanently remove the record.

## 3. Other planned endpoints

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/api/v1/departments` | Planned | List departments |
| GET | `/api/v1/departments/{id}/employees` | Planned | List employees in a department |

Do not treat planned endpoints as implemented until their routes and tests exist.

## 4. Request and response conventions

- Use JSON request and response bodies.
- Use appropriate HTTP status codes.
- Validate email addresses, required text, numeric ranges, and date values.
- Enforce unique employee IDs and work email addresses.
- Use pagination for employee list requests.
- Return clear error messages without exposing secrets or internal database details.
- Keep business rules in the service layer where applicable.

## 5. Authentication and authorization

Authentication and role-based authorization are not yet documented as implemented. Do not assume these routes are protected until authentication and authorization middleware or dependencies are configured and tested.

## 6. Dependency health and limitations

The database check attempts a real PostgreSQL connection. Redis and background-worker checks currently report `not_configured` because those integrations are not configured in this project. The overall health status therefore remains `degraded` until all required checks report healthy.

This contract documents the current Phase 1 implementation and distinguishes it from planned functionality. Update it alongside future API changes and tests.
