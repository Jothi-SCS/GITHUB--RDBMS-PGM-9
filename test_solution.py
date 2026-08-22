import mysql.connector
import subprocess
import re
import sys

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "CollegeDB"
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def read_solution():
    try:
        with open("solution.sql", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("ERROR: solution.sql not found.")
        sys.exit(1)


def test_department_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'CollegeDB'
        AND table_name = 'Department'
    """)

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, "Department table does not exist."
    print("PASS: Department table exists.")


def test_student_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'CollegeDB'
        AND table_name = 'Student'
    """)

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 1, "Student table does not exist."
    print("PASS: Student table exists.")


def test_department_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Department")
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 3, f"Expected 3 departments, found {result}."
    print("PASS: Department table contains 3 records.")


def test_student_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Student")
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert result == 4, f"Expected 4 students, found {result}."
    print("PASS: Student table contains 4 records.")


def test_inner_join_keyword():
    solution = read_solution()

    assert re.search(
        r"\bINNER\s+JOIN\b",
        solution,
        re.IGNORECASE
    ), "INNER JOIN keyword is missing."

    print("PASS: INNER JOIN found in solution.sql.")


def test_join_query():
    solution = read_solution()

    # Remove comments
    solution_clean = re.sub(r'--.*', '', solution)

    # Find SELECT statement
    match = re.search(
        r'(SELECT[\s\S]*?;)',
        solution_clean,
        re.IGNORECASE
    )

    assert match, "No SELECT query found in solution.sql."

    query = match.group(1)

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        raise AssertionError(f"SQL query failed: {e}")

    cursor.close()
    conn.close()

    expected = [
        ("Arun", "Computer Science"),
        ("Divya", "Mathematics"),
        ("Karthik", "Computer Science"),
        ("Nisha", "Physics")
    ]

    actual = [
        (str(row[0]), str(row[1]))
        for row in rows
    ]

    assert actual == expected, (
        f"\nExpected:\n{expected}\n\nActual:\n{actual}"
    )

    print("PASS: INNER JOIN produced the correct output.")


if __name__ == "__main__":

    print("Starting SQL Autograding...\n")

    test_department_table()
    test_student_table()
    test_department_records()
    test_student_records()
    test_inner_join_keyword()
    test_join_query()

    print("\n====================================")
    print("ALL TESTS PASSED!")
    print("====================================")
