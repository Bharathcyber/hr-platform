# Employee Data Model - Task 2

```mermaid
erDiagram
    DEPARTMENTS ||--o{ ROLES : contains
    DEPARTMENTS ||--o{ EMPLOYEES : has
    ROLES ||--o{ EMPLOYEES : assigned_currently
    EMPLOYEES o|--o{ EMPLOYEES : manages
    EMPLOYEES ||--o{ EMPLOYEE_ASSIGNMENTS : has_history
    DEPARTMENTS o|--o{ EMPLOYEE_ASSIGNMENTS : historical_department
    ROLES o|--o{ EMPLOYEE_ASSIGNMENTS : historical_role
    EMPLOYEES o|--o{ EMPLOYEE_ASSIGNMENTS : historical_manager

    DEPARTMENTS {
        string department_id PK
        string department_name
        string cost_center
        string description
    }

    ROLES {
        string role_id PK
        string department_id FK
        string role_title
        string level
        string grade
    }

    EMPLOYEES {
        string employee_id PK
        string full_name
        string work_email UK
        date hire_date
        date exit_date
        string department_id
        string role_id
        string manager_id
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    EMPLOYEE_ASSIGNMENTS {
        string assignment_id PK
        string employee_id FK
        datetime effective_from
        datetime effective_to
        string department_id FK
        string role_id FK
        int job_level
        string manager_id FK
        string change_reason
    }