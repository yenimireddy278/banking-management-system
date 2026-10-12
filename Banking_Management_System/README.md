# Banking Management System (Python + SQLite)

A command-line banking management project for learning and portfolio use. It supports account creation, deposits, withdrawals, balance enquiry, account listing, and transaction history. Account and transaction data are saved in SQLite.

## Requirements
- Python 3.10 or newer recommended
- No third-party packages required (uses Python standard library)

## Run
1. Extract the ZIP file.
2. Open a terminal or Command Prompt in the extracted `Banking_Management_System` folder.
3. Run:

   ```bash
   python main.py
   ```

   On some Windows installations, use `py main.py`.

The database file `banking.db` is created automatically in the current working directory.

## Menu
1. Create account
2. Deposit money
3. Withdraw money
4. Balance enquiry
5. Transaction history
6. List accounts
0. Exit

## Run tests
From the project folder, run:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database and do not alter your personal `banking.db`.

## Project structure
```text
Banking_Management_System/
├── main.py
├── banking.py
├── README.md
└── tests/
    └── test_banking.py
```

## Resume description (use after you run and verify it)
**Banking Management System | Python, SQLite**
- Built a command-line banking application supporting customer account creation, deposits, withdrawals, and balance enquiry.
- Stored account details and transaction records in SQLite, with transaction history and balance tracking.
- Added input validation and safeguards against invalid amounts and insufficient-balance withdrawals.

## Important note
This is an educational demonstration, not production banking software. It does not implement authentication, authorization, encryption, audit-grade logging, or real bank integrations. Do not use real customer or financial data.
