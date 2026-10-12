from banking import BankingSystem


def read_amount(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid number.")


def main():
    bank = BankingSystem()
    print("\n=== Banking Management System ===")
    try:
        while True:
            print("\n1. Create account")
            print("2. Deposit money")
            print("3. Withdraw money")
            print("4. Balance enquiry")
            print("5. Transaction history")
            print("6. List accounts")
            print("0. Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                name = input("Customer full name: ").strip()
                if not name:
                    print("Name cannot be empty.")
                    continue
                phone = input("Phone number (optional): ").strip()
                account_no = bank.create_account(name, phone)
                print(f"Account created successfully. Account number: {account_no}")
            elif choice == "2":
                account_no = input("Account number: ").strip()
                amount = read_amount("Deposit amount: ")
                bank.deposit(account_no, amount)
                print("Deposit successful.")
            elif choice == "3":
                account_no = input("Account number: ").strip()
                amount = read_amount("Withdrawal amount: ")
                bank.withdraw(account_no, amount)
                print("Withdrawal successful.")
            elif choice == "4":
                account_no = input("Account number: ").strip()
                account = bank.get_account(account_no)
                print(f"Account holder: {account['name']}")
                print(f"Balance: ₹{account['balance']:.2f}")
            elif choice == "5":
                account_no = input("Account number: ").strip()
                transactions = bank.get_transactions(account_no)
                if not transactions:
                    print("No transactions found.")
                else:
                    print("\nDate/time                 Type        Amount       Balance after")
                    print("-" * 68)
                    for txn in transactions:
                        print(
                            f"{txn['created_at']:<25} "
                            f"{txn['transaction_type']:<11} "
                            f"₹{txn['amount']:>9.2f} "
                            f"₹{txn['balance_after']:>12.2f}"
                        )
            elif choice == "6":
                accounts = bank.list_accounts()
                if not accounts:
                    print("No accounts have been created.")
                for account in accounts:
                    print(
                        f"{account['account_no']} | {account['name']} | "
                        f"Balance: ₹{account['balance']:.2f}"
                    )
            elif choice == "0":
                print("Thank you for using the Banking Management System.")
                break
            else:
                print("Invalid option. Choose one of the listed options.")
    except (ValueError, LookupError) as exc:
        print(f"Error: {exc}")
        print("Returning to the main menu is recommended; restart the program if needed.")
    finally:
        bank.close()


if __name__ == "__main__":
    main()
