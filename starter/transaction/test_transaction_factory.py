import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_factory import TransactionFactory


class TestTransactionFactory(unittest.TestCase):

    def test_create_income(self):
        t = TransactionFactory.create_income(100)
        self.assertEqual(t, Transaction(100, TransactionCategory.INCOME))

    def test_create_expense(self):
        t = TransactionFactory.create_expense(40)
        self.assertEqual(t, Transaction(40, TransactionCategory.EXPENSE))

    def test_create_from_dict_with_enum_value(self):
        t = TransactionFactory.create_from_dict(
            {"amount": 75, "category": "Income"}
        )
        self.assertEqual(t, Transaction(75, TransactionCategory.INCOME))

    def test_create_from_dict_with_enum_name(self):
        t = TransactionFactory.create_from_dict(
            {"amount": 30, "category": "EXPENSE"}
        )
        self.assertEqual(t, Transaction(30, TransactionCategory.EXPENSE))

    def test_create_from_dict_unknown_category_raises(self):
        with self.assertRaises(ValueError):
            TransactionFactory.create_from_dict(
                {"amount": 10, "category": "Bonus"}
            )

    def test_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            TransactionFactory.create_income(-5)

    def test_missing_amount_raises(self):
        with self.assertRaises(ValueError):
            TransactionFactory.create_from_dict({"category": "Income"})


if __name__ == "__main__":
    unittest.main()
