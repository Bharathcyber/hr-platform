
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(201) NOT NULL,
    work_email VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(30),
    date_of_birth DATE,
    hire_date DATE,
    exit_date DATE,
    employment_status VARCHAR(30) NOT NULL,
    employment_type VARCHAR(30),
    department_id VARCHAR(20),
    role_id VARCHAR(20),
    manager_id VARCHAR(20),
    work_location VARCHAR(100),
    work_mode VARCHAR(30),
    highest_education VARCHAR(150),
    prior_experience_years INTEGER NOT NULL DEFAULT 0,
    career_gap_months INTEGER NOT NULL DEFAULT 0,
    commute_distance_km NUMERIC(7, 2),
    pf_applicable CHAR(1),
    esi_applicable CHAR(1),
    notice_period_days INTEGER,
    resignation_date DATE,
    exit_type VARCHAR(50),
    exit_reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT chk_prior_experience
        CHECK (prior_experience_years >= 0),

    CONSTRAINT chk_career_gap
        CHECK (career_gap_months >= 0),

    CONSTRAINT chk_notice_period
        CHECK (notice_period_days IS NULL OR notice_period_days >= 0),

    CONSTRAINT chk_pf_applicable
        CHECK (pf_applicable IS NULL OR pf_applicable IN ('Y', 'N')),

    CONSTRAINT chk_esi_applicable
        CHECK (esi_applicable IS NULL OR esi_applicable IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_employees_department_id
    ON employees(department_id);

CREATE INDEX IF NOT EXISTS idx_employees_employment_status
    ON employees(employment_status);
