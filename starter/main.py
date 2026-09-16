"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_factory import TransactionFactory


def main():
    print("Adding transactions...")

    # Create balance and add observers
    balance = Balance.get_instance()
    balance.reset()
    balance.register_observer(PrintObserver())
    balance.register_observer(LowBalanceAlertObserver(threshold=100))

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create a couple of transactions via the TransactionFactory (Factory
    # Method pattern) to show it producing the same Transaction objects the
    # rest of the app already understands, e.g. from raw input like a CSV
    # row or API payload.
    transactions.append(TransactionFactory.create_expense(120))
    transactions.append(
        TransactionFactory.create_from_dict(
            {"amount": 30, "category": "Income"}
        )
    )

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # Apply all transactions to balance
    for transaction in all_transactions:
        balance.apply_transaction(transaction)

    print(balance.summary())


if __name__ == "__main__":
    main()
