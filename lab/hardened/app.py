"""Correção do exemplo: consulta parametrizada, sem servidor ou dados reais."""

import sqlite3


def create_database():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    connection.executemany(
        "INSERT INTO users (name) VALUES (?)", [("Ana Demo",), ("Bruno Demo",)]
    )
    return connection


def find_user(connection, name):
    return connection.execute(
        "SELECT id, name FROM users WHERE name = ?", (name,)
    ).fetchall()


if __name__ == "__main__":
    database = create_database()
    try:
        print("Busca normal:", find_user(database, "Ana Demo"))
        print("Entrada adversarial local:", find_user(database, "' OR '1'='1"))
    finally:
        database.close()
