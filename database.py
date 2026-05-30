"""SQLite database setup and connection helpers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config import (
    DATABASE_PATH,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    ensure_directories,
)
from utils.helpers import hash_password


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


class Database:
    """Small wrapper around SQLite connection creation and schema setup."""

    def __init__(self, db_path: Path | str = DATABASE_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """Return a configured SQLite connection."""
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON;")
            return connection
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not connect to database: {exc}") from exc

    def initialize(self) -> None:
        """Create required tables and seed the default admin user."""
        ensure_directories()
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity >= 0),
                    price REAL NOT NULL CHECK (price >= 0),
                    created_date TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
                    sale_amount REAL NOT NULL CHECK (sale_amount >= 0),
                    sale_date TEXT NOT NULL,
                    FOREIGN KEY (product_id)
                        REFERENCES products (product_id)
                        ON DELETE RESTRICT
                );
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO users (username, password)
                VALUES (?, ?);
                """,
                (DEFAULT_ADMIN_USERNAME, hash_password(DEFAULT_ADMIN_PASSWORD)),
            )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection for explicit transactional use."""
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except sqlite3.Error as exc:
            connection.rollback()
            raise DatabaseError(f"Database transaction failed: {exc}") from exc
        finally:
            connection.close()


def initialize_database(db_path: Path | str = DATABASE_PATH) -> Database:
    """Initialize the SQLite database and return the Database wrapper."""
    database = Database(db_path)
    database.initialize()
    return database
