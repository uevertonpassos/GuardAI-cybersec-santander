"""Exemplo intencionalmente vulnerável. Apenas SQLite em memória e dados fictícios."""

import sqlite3


def create_database():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    connection.executemany(
        "INSERT INTO users (name) VALUES (?)", [("Ana Demo",), ("Bruno Demo",)]
    )
    return connection


def find_user(connection, name):
    # Falha didática: a entrada passa a fazer parte da instrução SQL.
    return connection.execute(f"SELECT id, name FROM users WHERE name = '{name}'").fetchall()


if __name__ == "__main__":
    database = create_database()
    try:
        print("Busca normal:", find_user(database, "Ana Demo"))
        print("Entrada adversarial local:", find_user(database, "' OR '1'='1"))
    finally:
        database.close()
