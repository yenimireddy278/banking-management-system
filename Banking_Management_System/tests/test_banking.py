import tempfile
import unittest
from pathlib import Path

from banking import BankingSystem


class BankingSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_banking.db"
        self.bank = BankingSystem(self.db_path)
        self.account = self.bank.create_account("Test Customer", "9999999999")

    def tearDown(self):
        self.bank.close()
        self.temp_dir.cleanup()

    def test_new_account_starts_at_zero(self):
        self.assertEqual(self.bank.get_account(self.account)["balance"], 0.0)

    def test_deposit_and_withdraw(self):
        self.bank.deposit(self.account, "100.50")
        self.bank.withdraw(self.account, "25.25")
        self.assertEqual(self.bank.get_account(self.account)["balance"], 75.25)

    def test_reject_insufficient_balance(self):
        with self.assertRaisesRegex(ValueError, "Insufficient balance"):
            self.bank.withdraw(self.account, 10)

    def test_reject_non_positive_amount(self):
        with self.assertRaises(ValueError):
            self.bank.deposit(self.account, 0)
        with self.assertRaises(ValueError):
            self.bank.withdraw(self.account, -5)

    def test_reject_unknown_account(self):
        with self.assertRaises(LookupError):
            self.bank.get_account("AC00000000")

    def test_transaction_history(self):
        self.bank.deposit(self.account, 50)
        self.bank.withdraw(self.account, 20)
        history = self.bank.get_transactions(self.account)
        self.assertEqual([t["transaction_type"] for t in history], ["DEPOSIT", "WITHDRAWAL"])
        self.assertEqual([t["balance_after"] for t in history], [50.0, 30.0])

    def test_name_required(self):
        with self.assertRaises(ValueError):
            self.bank.create_account("   ")


if __name__ == "__main__":
    unittest.main()
