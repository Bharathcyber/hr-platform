
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.models import Department, Role


BASE_DIR = Path(__file__).resolve().parent.parent
WORKBOOK_PATH = BASE_DIR / "01_LedgerForge_Python_Master_Dataset.xlsx"


def read_sheet(workbook, sheet_name):
    worksheet = workbook[sheet_name]
    rows = worksheet.iter_rows(values_only=True)

    headers = next(rows)
    headers = [str(value).strip() if value is not None else "" for value in headers]

    records = []
    for row in rows:
        if not any(value is not None for value in row):
            continue
        records.append(dict(zip(headers, row)))

    return records


def required_text(value, field, sheet_name):
    if value is None or not str(value).strip():
        raise ValueError(f"{sheet_name}: missing required value for {field}")
    return str(value).strip()


def main():
    if not WORKBOOK_PATH.is_file():
        raise FileNotFoundError(f"Workbook not found: {WORKBOOK_PATH}")

    workbook = load_workbook(
        WORKBOOK_PATH,
        read_only=True,
        data_only=True,
    )

    try:
        department_rows = read_sheet(workbook, "departments")
        role_rows = read_sheet(workbook, "roles")
    finally:
        workbook.close()

    departments = []
    department_ids = set()

    for row in department_rows:
        department_id = required_text(
            row.get("department_id"), "department_id", "departments"
        )
        department_name = required_text(
            row.get("department_name"), "department_name", "departments"
        )

        if department_id in department_ids:
            raise ValueError(f"Duplicate department_id in workbook: {department_id}")
        department_ids.add(department_id)

        departments.append(
            {
                "department_id": department_id,
                "department_name": department_name,
                "cost_center": (
                    str(row["cost_center"]).strip()
                    if row.get("cost_center") is not None
                    else None
                ),
                "description": (
                    str(row["description"]).strip()
                    if row.get("description") is not None
                    else None
                ),
            }
        )

    roles = []
    role_ids = set()

    for row in role_rows:
        role_id = required_text(row.get("role_id"), "role_id", "roles")
        department_id = required_text(
            row.get("department_id"), "department_id", "roles"
        )
        role_title = required_text(row.get("role_title"), "role_title", "roles")

        if role_id in role_ids:
            raise ValueError(f"Duplicate role_id in workbook: {role_id}")
        role_ids.add(role_id)

        if department_id not in department_ids:
            raise ValueError(
                f"Role {role_id} references missing workbook department {department_id}"
            )

        overtime_value = str(row.get("overtime_eligible") or "").strip().upper()
        if overtime_value not in {"Y", "N", "TRUE", "FALSE"}:
            raise ValueError(
                f"Role {role_id} has unexpected overtime_eligible value: "
                f"{overtime_value!r}"
            )

        roles.append(
            {
                "role_id": role_id,
                "department_id": department_id,
                "role_title": role_title,
                "level": (
                    str(row["level"]).strip()
                    if row.get("level") is not None
                    else None
                ),
                "grade": (
                    str(row["grade"]).strip()
                    if row.get("grade") is not None
                    else None
                ),
                "band_min_annual": (
                    Decimal(str(row["band_min_annual"]))
                    if row.get("band_min_annual") is not None
                    else None
                ),
                "band_mid_annual": (
                    Decimal(str(row["band_mid_annual"]))
                    if row.get("band_mid_annual") is not None
                    else None
                ),
                "band_max_annual": (
                    Decimal(str(row["band_max_annual"]))
                    if row.get("band_max_annual") is not None
                    else None
                ),
                "overtime_eligible": overtime_value in {"Y", "TRUE"},
                "band_year": (
                    int(row["band_year"])
                    if row.get("band_year") is not None
                    else None
                ),
            }
        )

    engine = create_engine(settings.database_url)

    try:
        with engine.begin() as connection:
            # Upsert departments first because roles reference them.
            department_table = Department.__table__
            department_statement = insert(department_table).values(departments)
            department_statement = department_statement.on_conflict_do_update(
                index_elements=["department_id"],
                set_={
                    "department_name": department_statement.excluded.department_name,
                    "cost_center": department_statement.excluded.cost_center,
                    "description": department_statement.excluded.description,
                },
            )
            connection.execute(department_statement)

            role_table = Role.__table__
            role_statement = insert(role_table).values(roles)
            role_statement = role_statement.on_conflict_do_update(
                index_elements=["role_id"],
                set_={
                    "department_id": role_statement.excluded.department_id,
                    "role_title": role_statement.excluded.role_title,
                    "level": role_statement.excluded.level,
                    "grade": role_statement.excluded.grade,
                    "band_min_annual": role_statement.excluded.band_min_annual,
                    "band_mid_annual": role_statement.excluded.band_mid_annual,
                    "band_max_annual": role_statement.excluded.band_max_annual,
                    "overtime_eligible": role_statement.excluded.overtime_eligible,
                    "band_year": role_statement.excluded.band_year,
                },
            )
            connection.execute(role_statement)

            department_count = connection.scalar(
                select(func.count()).select_from(department_table)
            )
            role_count = connection.scalar(
                select(func.count()).select_from(role_table)
            )
            employee_count = connection.scalar(
                select(func.count()).select_from(
                    Department.metadata.tables["employees"]
                )
            )

        print("Master-data seed completed successfully.")
        print(f"Workbook departments: {len(departments)}")
        print(f"Workbook roles: {len(roles)}")
        print(f"Departments in database: {department_count}")
        print(f"Roles in database: {role_count}")
        print(f"Employees preserved: {employee_count}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
