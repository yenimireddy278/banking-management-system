"""Core banking operations backed by SQLite.

This is an educational demo, not a production banking system.
It stores money as integer paise internally to avoid floating-point rounding errors.
"""
from __future__ import annotations

import sqlite3
import secrets
from datetime import datetime
from pathlib import Path


class BankingSystem:
    def __init__(self, db_path: str | Path = "banking.db"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_no TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL DEFAULT '',
                    balance_paise INTEGER NOT NULL DEFAULT 0 CHECK(balance_paise >= 0),
                    created_at TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_no TEXT NOT NULL,
                    transaction_type TEXT NOT NULL
                        CHECK(transaction_type IN ('DEPOSIT', 'WITHDRAWAL')),
                    amount_paise INTEGER NOT NULL CHECK(amount_paise > 0),
                    balance_after_paise INTEGER NOT NULL CHECK(balance_after_paise >= 0),
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(account_no) REFERENCES accounts(account_no)
                )
            """)

    @staticmethod
    def _to_paise(amount: float | int | str) -> int:
        try:
            value = round(float(amount) * 100)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("Enter a valid amount.") from None
        if value <= 0:
            raise ValueError("Amount must be greater than zero.")
        # Reject fractions smaller than one paisa.
        if abs(float(amount) * 100 - value) > 1e-7:
            raise ValueError("Amount can have at most two decimal places.")
        return value

    @staticmethod
    def _money(paise: int) -> float:
        return paise / 100

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def create_account(self, name: str, phone: str = "") -> str:
        name = (name or "").strip()
        phone = (phone or "").strip()
        if not name:
            raise ValueError("Customer name cannot be empty.")
        # Use a random account number and retry if the rare collision occurs.
        for _ in range(10):
            account_no = "AC" + "".join(secrets.choice("0123456789") for _ in range(8))
            try:
                with self.conn:
                    self.conn.execute(
                        "INSERT INTO accounts(account_no, name, phone, balance_paise, created_at) "
                        "VALUES (?, ?, ?, 0, ?)",
                        (account_no, name, phone, self._timestamp()),
                    )
                return account_no
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("Could not generate a unique account number. Please try again.")

    def _require_account(self, account_no: str) -> sqlite3.Row:
        account_no = (account_no or "").strip()
        if not account_no:
            raise ValueError("Account number cannot be empty.")
        row = self.conn.execute(
            "SELECT * FROM accounts WHERE account_no = ?", (account_no,)
        ).fetchone()
        if row is None:
            raise LookupError("Account not found. Check the account number.")
        return row

    def deposit(self, account_no: str, amount: float | int | str) -> float:
        paise = self._to_paise(amount)
        self._require_account(account_no)
        with self.conn:
            self.conn.execute(
                "UPDATE accounts SET balance_paise = balance_paise + ? WHERE account_no = ?",
                (paise, account_no.strip()),
            )
            balance = self.conn.execute(
                "SELECT balance_paise FROM accounts WHERE account_no = ?",
                (account_no.strip(),),
            ).fetchone()["balance_paise"]
            self.conn.execute(
                "INSERT INTO transactions(account_no, transaction_type, amount_paise, "
                "balance_after_paise, created_at) VALUES (?, 'DEPOSIT', ?, ?, ?)",
                (account_no.strip(), paise, balance, self._timestamp()),
            )
        return self._money(balance)

    def withdraw(self, account_no: str, amount: float | int | str) -> float:
        paise = self._to_paise(amount)
        account = self._require_account(account_no)
        if account["balance_paise"] < paise:
            raise ValueError("Insufficient balance.")
        with self.conn:
            # Conditional update also protects against a stale balance read.
            cursor = self.conn.execute(
                "UPDATE accounts SET balance_paise = balance_paise - ? "
                "WHERE account_no = ? AND balance_paise >= ?",
                (paise, account_no.strip(), paise),
            )
            if cursor.rowcount != 1:
                raise ValueError("Insufficient balance.")
            balance = self.conn.execute(
                "SELECT balance_paise FROM accounts WHERE account_no = ?",
                (account_no.strip(),),
            ).fetchone()["balance_paise"]
            self.conn.execute(
                "INSERT INTO transactions(account_no, transaction_type, amount_paise, "
                "balance_after_paise, created_at) VALUES (?, 'WITHDRAWAL', ?, ?, ?)",
                (account_no.strip(), paise, balance, self._timestamp()),
            )
        return self._money(balance)

    def get_account(self, account_no: str) -> dict:
        row = self._require_account(account_no)
        return {
            "account_no": row["account_no"],
            "name": row["name"],
            "phone": row["phone"],
            "balance": self._money(row["balance_paise"]),
            "created_at": row["created_at"],
        }

    def list_accounts(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM accounts ORDER BY created_at DESC, account_no"
        ).fetchall()
        return [
            {
                "account_no": row["account_no"],
                "name": row["name"],
                "phone": row["phone"],
                "balance": self._money(row["balance_paise"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_transactions(self, account_no: str) -> list[dict]:
        self._require_account(account_no)
        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE account_no = ? ORDER BY id",
            (account_no.strip(),),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "account_no": row["account_no"],
                "transaction_type": row["transaction_type"],
                "amount": self._money(row["amount_paise"]),
                "balance_after": self._money(row["balance_after_paise"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def close(self) -> None:
        self.conn.close()
