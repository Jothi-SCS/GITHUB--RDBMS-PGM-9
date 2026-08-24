import mysql.connector
import sys
import os
import pytest

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root"
}

DATABASE = "CollegeDB"
STUDENT_FILE = "answer.sql"


def connect_server():
    return mysql.connector.connect(**DB_CONFIG)


def connect_db():
    config = DB_CONFIG.copy()
    config["database"] = DATABASE
    return mysql.connector.connect(**config)


def execute_student_sql():
    if not os.path.exists(STUDENT_FILE):
        raise AssertionError(
            f"{STUDENT_FILE} not found. "
            f"Students must save their solution as {STUDENT_FILE}."
        )

    with open(STUDENT_FILE, "r", encoding="utf-8") as file:
        sql = file.read()

    if not sql.strip():
        raise AssertionError(f"{STUDENT_FILE} is empty.")

    conn = connect_server()
    cursor = conn.cursor()

    try:
        statements = [s.strip() for s in sql.split(";") if s.strip()]

        for statement in statements:
            cursor.execute(statement)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise AssertionError(
            f"Student SQL execution failed: {e}"
        )

    finally:
        cursor.close()
        conn.close()


def test_database_exists():
    conn = connect_server()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.schemata
        WHERE schema_name = %s
        """,
        (DATABASE,)
    )

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, "CollegeDB database does not exist."


def test_department_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name = 'Department'
        """,
        (DATABASE,)
    )

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, "Department table does not exist."


def test_student_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name = 'Student'
        """,
        (DATABASE,)
    )

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, "Student table does not exist."


def test_department_columns():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name = 'Department'
        ORDER BY ORDINAL_POSITION
        """,
        (DATABASE,)
    )

    columns = cursor.fetchall()

    cursor.close()
    conn.close()

    expected = [
        ("DepartmentID", "int"),
        ("DepartmentName", "varchar")
    ]

    actual = [(row[0], row[1]) for row in columns]

    assert actual == expected, (
        f"Incorrect Department columns.\n"
        f"Expected: {expected}\n"
        f"Actual: {actual}"
    )


def test_student_columns():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name = 'Student'
        ORDER BY ORDINAL_POSITION
        """,
        (DATABASE,)
    )

    columns = cursor.fetchall()

    cursor.close()
    conn.close()

    expected = [
        ("StudentID", "int"),
        ("StudentName", "varchar"),
        ("DepartmentID", "int")
    ]

    actual = [(row[0], row[1]) for row in columns]

    assert actual == expected, (
        f"Incorrect Student columns.\n"
        f"Expected: {expected}\n"
        f"Actual: {actual}"
    )


def test_primary_keys():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM information_schema.key_column_usage
        WHERE table_schema = %s
        AND table_name = 'Department'
        AND constraint_name = 'PRIMARY'
        """
        ,
        (DATABASE,)
    )

    department_pk = [row[0] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM information_schema.key_column_usage
        WHERE table_schema = %s
        AND table_name = 'Student'
        AND constraint_name = 'PRIMARY'
        """,
        (DATABASE,)
    )

    student_pk = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    assert department_pk == ["DepartmentID"], \
        "DepartmentID must be the primary key."

    assert student_pk == ["StudentID"], \
        "StudentID must be the primary key."


def test_foreign_key():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.key_column_usage
        WHERE table_schema = %s
        AND table_name = 'Student'
        AND column_name = 'DepartmentID'
        AND referenced_table_name = 'Department'
        AND referenced_column_name = 'DepartmentID'
        """,
        (DATABASE,)
    )

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, (
        "Student.DepartmentID must reference "
        "Department.DepartmentID."
    )


def test_department_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DepartmentID, DepartmentName
        FROM Department
        ORDER BY DepartmentID
        """
    )

    actual = cursor.fetchall()

    expected = [
        (101, "Computer Science"),
        (102, "Mathematics"),
        (103, "Physics")
    ]

    cursor.close()
    conn.close()

    assert actual == expected, (
        f"\nExpected Department records:\n{expected}"
        f"\n\nActual:\n{actual}"
    )


def test_student_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT StudentID, StudentName, DepartmentID
        FROM Student
        ORDER BY StudentID
        """
    )

    actual = cursor.fetchall()

    expected = [
        (1001, "Arun", 101),
        (1002, "Divya", 102),
        (1003, "Karthik", 101),
        (1004, "Nisha", 103)
    ]

    cursor.close()
    conn.close()

    assert actual == expected, (
        f"\nExpected Student records:\n{expected}"
        f"\n\nActual:\n{actual}"
    )


def test_inner_join():
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT Student.StudentName, Department.DepartmentName
        FROM Student
        INNER JOIN Department
        ON Student.DepartmentID = Department.DepartmentID
        ORDER BY Student.StudentID
    """

    cursor.execute(query)
    actual = cursor.fetchall()

    expected = [
        ("Arun", "Computer Science"),
        ("Divya", "Mathematics"),
        ("Karthik", "Computer Science"),
        ("Nisha", "Physics")
    ]

    cursor.close()
    conn.close()

    assert actual == expected, (
        f"\nExpected JOIN output:\n{expected}"
        f"\n\nActual:\n{actual}"
    )


if __name__ == "__main__":

    print("====================================")
    print("Starting SQL Autograding")
    print("====================================")

    try:
        execute_student_sql()

        test_database_exists()
        test_department_table()
        test_student_table()
        test_department_columns()
        test_student_columns()
        test_primary_keys()
        test_foreign_key()
        test_department_records()
        test_student_records()
        test_inner_join()

        print("\n====================================")
        print("ALL TESTS PASSED!")
        print("====================================")

    except AssertionError as e:
        print("\n====================================")
        print("TEST FAILED")
        print("====================================")
        print(e)
        sys.exit(1)

    except Exception as e:
        print("\n====================================")
        print("AUTOGRADING ERROR")
        print("====================================")
        print(e)
        sys.exit(1)
