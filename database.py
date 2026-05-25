import sqlite3
import os

# CREATE DATABASE FOLDER

os.makedirs("database", exist_ok=True)

# DATABASE CONNECTION

conn = sqlite3.connect(
    "database/expenses.db",
    check_same_thread=False
)

cursor = conn.cursor()

# CREATE TABLE

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """
)

conn.commit()

# ADD EXPENSE

def add_expense(date, category, amount, description):

    cursor.execute(
        """
        INSERT INTO expenses
        (date, category, amount, description)
        VALUES (?, ?, ?, ?)
        """,
        (date, category, amount, description)
    )

    conn.commit()

# FETCH EXPENSES

def fetch_expenses():

    cursor.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    )

    rows = cursor.fetchall()

    return rows

# DELETE EXPENSE

def delete_expense(expense_id):

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()

    return cursor.rowcount