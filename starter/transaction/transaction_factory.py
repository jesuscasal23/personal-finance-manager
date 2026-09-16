# transaction_factory.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionFactory:
    """
    Factory Method pattern: centralizes creation and validation of
    Transaction objects so callers never construct them directly from
    raw/untrusted input (e.g. a dict from a CSV row or a JSON payload).
    """

    @staticmethod
    def create_income(amount):
        """Create an INCOME transaction."""
        return TransactionFactory._create(amount, TransactionCategory.INCOME)

    @staticmethod
    def create_expense(amount):
        """Create an EXPENSE transaction."""
        return TransactionFactory._create(
            amount, TransactionCategory.EXPENSE
        )

    @staticmethod
    def create_from_dict(data):
        """
        Create a Transaction from a raw dict, e.g.
        {"amount": 50, "category": "Income"}.
        Raises ValueError if the category is missing or unrecognized.
        """
        amount = data.get("amount")
        category_value = data.get("category")

        category = None
        for member in TransactionCategory:
            if category_value in (member.value, member.name):
                category = member
                break

        if category is None:
            raise ValueError(
                f"Unrecognized transaction category: {category_value!r}"
            )

        return TransactionFactory._create(amount, category)

    @staticmethod
    def _create(amount, category):
        if amount is None or amount < 0:
            raise ValueError(
                f"Transaction amount must be a non-negative number, "
                f"got {amount!r}"
            )
        return Transaction(amount, category)
