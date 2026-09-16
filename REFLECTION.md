# Reflection

## The Four Design Patterns

### 1. Singleton — `balance/balance.py`
`Balance` is the single source of truth for the user's net balance, so it must never
exist as two independent copies with drifting state. `Balance.get_instance()` lazily
creates the one instance and returns it on every subsequent call. Every observer,
transaction, and the `main.py` demo script all read and write through that same object.

**Why it fits:** a finance app with two different "current balances" floating around
is a correctness bug waiting to happen. Singleton makes "there is exactly one balance"
a guarantee enforced by the class itself, not a convention callers have to remember.

**Trade-off:** Singletons introduce global mutable state, which makes tests order-
dependent unless you're careful. Every test in `test_balance.py` and
`test_balance_observer.py` has to call `Balance.get_instance().reset()` in `setUp()` to
avoid leaking balance/state between test cases — that's the price of the pattern.

### 2. Adapter — `transaction/transaction_adapter.py`
`ExternalFreelanceIncome` represents data shaped by a third-party platform (invoice ID,
project description, a `typ` field) — a shape `Balance` was never designed to understand.
`TransactionAdapter` wraps an `ExternalFreelanceIncome` and exposes `to_transaction()`,
translating it into a plain `Transaction(amount, TransactionCategory.INCOME)`.

**Why it fits:** it lets the core app (`Balance`, `Transaction`) stay ignorant of every
external data source it might ever need to support. Adding a second freelance platform
with a different payload shape later means writing a second adapter, not touching
`Balance` at all.

**Trade-off:** the current adapter is intentionally narrow — it always maps to `INCOME`
and discards the invoice ID/description. That's correct for this app's needs today, but
if reporting ever needed to show "which invoice funded this transaction," the adapter
(or `Transaction` itself) would need to grow to carry that metadata through.

### 3. Observer — `balance/balance_observer.py`
`Balance.apply_transaction()` updates the balance and then calls `_notify_observers()`,
which loops through every registered `IBalanceObserver` and calls `update(balance,
transaction)`. `PrintObserver` logs every change; `LowBalanceAlertObserver` tracks whether
the balance is currently under a threshold via `self.alert_triggered`.

**Why it fits:** `Balance` shouldn't need to know *what* should happen when it changes —
only that something might want to know. Adding a new reaction to balance changes (e.g., a
future `EmailAlertObserver`) means writing a new class and registering it, with zero
changes to `Balance`.

**Trade-off:** indirection. Reading `main.py` alone doesn't tell you everything that
happens when a transaction is applied — you have to know which observers were registered
elsewhere to predict the full behavior. For a small app this is manageable; in a larger
one it's worth documenting which observers exist and why.

### 4. Factory Method — `transaction/transaction_factory.py` (student's choice)

**Why chosen:** Singleton, Adapter, and Observer were already used, so this had to be
something new. Transaction creation was scattered as bare `Transaction(amount, category)`
calls with no validation — that's fine for hardcoded demo data, but risky once
transactions come from anywhere less trusted (a CSV import, a form, an API request).

**Where it fits:** `TransactionFactory` sits in front of `Transaction`'s constructor. It
offers `create_income()`, `create_expense()`, and `create_from_dict()` (which accepts
either the enum's name or its value as a string), and centralizes validation — e.g.
rejecting a missing or negative amount, or an unrecognized category — in one place
(`_create`) instead of repeating it wherever a `Transaction` gets built.

**How it improves flexibility/testability/scalability:** callers no longer need to know
how to validate raw input into a valid `Transaction` — they ask the factory and either
get a valid object or a clear `ValueError`. If `Transaction` construction rules ever
change (e.g., a new required field), only the factory needs updating, not every call
site. It's also trivially testable in isolation (`test_transaction_factory.py`) without
touching `Balance` at all.

## Dependency Injection

`LowBalanceAlertObserver(threshold)` takes its threshold via the constructor instead of
hardcoding a value, and `Balance.register_observer()` accepts any object satisfying the
`IBalanceObserver` interface rather than being wired to concrete observer classes.
`TransactionAdapter` similarly takes the external transaction object it wraps as a
constructor argument. In each case, the dependency is handed in rather than constructed
internally, which is what makes it possible to swap in a test double (e.g., a fake
observer that just records calls) without modifying the class under test.

## Overall Trade-offs

The main cost across this design is indirection: understanding the full behavior of
"apply this transaction" now requires knowing about the Singleton's registered observers,
the Adapter translating external data, and (optionally) the Factory validating raw input,
rather than reading one linear function top to bottom. For an app this size that's a
reasonable price for the flexibility gained — but it's a trade-off that would need
re-evaluating if the app grew much larger, at which point clearer documentation of "what
observers exist and why" would become more important than it is today.
