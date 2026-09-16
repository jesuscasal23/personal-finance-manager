# Guide: Personal Finance Manager (Design Patterns Project)

This guide walks through completing the `starter/` project step by step. It explains
*what* each piece needs to do and *why*, but leaves the actual implementation to you —
this is graded work.

Repo layout:

```
personal-finance-manager/
├── README.md
├── LICENSE.txt
└── starter/
    ├── main.py
    ├── balance/
    │   ├── balance.py                 <- Singleton (TODO)
    │   ├── balance_observer.py        <- Observer (TODO)
    │   ├── test_balance.py            <- given, should pass once balance.py works
    │   └── test_balance_observer.py   <- given, should pass once observer works
    └── transaction/
        ├── transaction.py             <- TODO (__str__, __eq__)
        ├── transaction_category.py    <- already done (Enum)
        ├── transaction_adapter.py     <- Adapter (TODO)
        ├── external_income_transaction.py  <- already done
        ├── test_transaction.py        <- given
        └── test_transaction_adapter.py<- given
```

Run everything from inside `starter/` so the `balance.*` / `transaction.*` imports resolve:

```bash
cd starter
python3 -m unittest discover -v
python3 main.py
```

---

## Step 1 — `transaction/transaction.py`

`Transaction` already stores `amount` and `category` in `__init__`. You need to implement:

- `__str__` — the test expects exactly:
  `"Transaction($50, category='TransactionCategory.INCOME')"`
  Look at how `str(TransactionCategory.INCOME)` renders to match this format precisely.
- `__eq__` — two transactions are equal if `amount` and `category` both match. This is
  what lets `test_transaction_adapter.py` compare an adapted transaction to an expected
  `Transaction(...)` with `assertEqual`.

No design pattern here yet — this is plumbing the other steps depend on.

---

## Step 2 — Singleton: `balance/balance.py`

**Goal:** only one `Balance` ever exists, and every part of the app that asks for "the
balance" gets the same object.

Requirements driven by `test_balance.py`:

- `Balance.get_instance()` — a classmethod/staticmethod that creates the instance on
  first call and returns the *same* instance on every later call
  (`test_singleton_instance` asserts `balance1 is balance2`).
- Direct construction (`Balance()`) should still work structurally, but the pattern is
  really enforced through `get_instance()` — decide whether you also want to guard
  `__init__`/`__new__` against creating a second usable instance (classic Singleton
  approaches: override `__new__`, or a module-level private instance with a factory
  classmethod — either is acceptable, just be consistent and be ready to explain the
  choice in your reflection).
- `reset()` — sets balance back to `0.0`.
- `add_income(amount)` / `add_expense(amount)` — increase/decrease the internal balance.
- `apply_transaction(transaction)` — dispatch based on `transaction.category`:
  - `TransactionCategory.INCOME` → call `add_income`
  - `TransactionCategory.EXPENSE` → call `add_expense`
  - anything else → `raise ValueError(...)` (see `test_apply_transaction_invalid_category`)
- `get_balance()` — returns the current numeric balance.
- `summary()` — returns a human-readable string (not exercised by the given tests, but
  required by the rubric/spec — keep it simple, e.g. `f"Current balance: ${self._balance:.2f}"`).

**This is also where Observer plugs in** (Step 3): `Balance` needs to hold a list of
registered observers and a `register_observer(observer)` method (used by
`test_balance_observer.py`), and `apply_transaction` needs to notify all observers
*after* updating the balance, passing the new balance and the transaction that caused
the change: `observer.update(self.get_balance(), transaction)`.

---

## Step 3 — Observer: `balance/balance_observer.py`

**Goal:** decouple "the balance changed" from "what should happen as a result"
(printing, alerting, anything else you bolt on later) — `Balance` shouldn't need to know
observers exist beyond the `update(balance, transaction)` interface.

`IBalanceObserver` (the interface) is already given.

- `PrintObserver.update(self, balance, transaction)` — print a message reflecting the
  new balance and/or the transaction that triggered it. Free-form format, just make it
  informative.
- `LowBalanceAlertObserver.update(self, balance, transaction)` — compare `balance` to
  `self.threshold`. Trace through `test_alert_triggers_on_low_balance` carefully:
  - it checks an `observer.alert_triggered` boolean attribute after each transaction
  - the flag must flip to `True` the moment balance drops below threshold, and flip back
    to `False` once balance rises back above threshold (it's not "sticky" — it reflects
    current state, re-evaluated on every update)
  - you'll need to initialize `self.alert_triggered = False` in `__init__`, and printing
    an alert message is a nice touch but the test only checks the flag

Wire registration in `main.py` (Step 5): create the `Balance` singleton, then
`register_observer` a `PrintObserver()` and a `LowBalanceAlertObserver(threshold=...)`
before applying any transactions.

---

## Step 4 — Adapter: `transaction/transaction_adapter.py`

**Goal:** `ExternalFreelanceIncome` (amount, invoice_id, description, fixed `typ="income"`)
is a shape the rest of the app doesn't understand. `TransactionAdapter` translates it into
a `Transaction` the `Balance` class knows how to apply — without `Balance` or `Transaction`
ever needing to know `ExternalFreelanceIncome` exists.

- `TransactionAdapter.__init__` already stores `self.external_transaction`.
- `to_transaction(self)` — read `self.external_transaction.amount` and produce
  `Transaction(amount, TransactionCategory.INCOME)`. (`test_adapter_converts_freelance_income`
  expects exactly this — freelance income always maps to `INCOME`.)

If you want to keep the invoice/description context instead of discarding it, that's a
reasonable enhancement to mention in your reflection (e.g., an extended `Transaction`
subclass or a note in `summary()`), but it's not required by the given tests.

---

## Step 5 — Wire it up in `main.py`

Replace the two `# TODO` comments:

1. **Create balance and add observers**
   ```python
   balance = Balance.get_instance()
   balance.register_observer(PrintObserver())
   balance.register_observer(LowBalanceAlertObserver(threshold=100))
   ```
   (pick whatever threshold makes the demo interesting given the transaction amounts
   already in the file).

2. **Apply all transactions to balance**
   ```python
   for txn in all_transactions:
       balance.apply_transaction(txn)
   print(balance.summary())
   ```

Run `python3 main.py` from `starter/` and confirm you see print statements for each
transaction and at least one low-balance alert firing given the sample data (adjust the
threshold or transactions if none trigger).

---

## Step 6 — Your Fourth Pattern (Student's Choice)

Pick one pattern **not already used** (Singleton, Adapter, Observer are taken). Common
good fits for this app:

- **Factory Method / Simple Factory** — a `TransactionFactory` that creates `Transaction`
  objects from raw dicts/CSV rows, centralizing validation/creation logic instead of
  scattering `Transaction(...)` calls everywhere.
- **Strategy** — pluggable alerting or categorization strategies (e.g., different
  low-balance policies: percentage-of-average vs. fixed threshold), injected into
  `LowBalanceAlertObserver` or `Balance`.
- **Decorator** — wrap `Transaction` objects to add behavior (e.g., a `TaxableTransaction`
  decorator that adjusts the effective amount) without modifying `Transaction` itself.
- **Command** — represent "apply this transaction" as a command object, enabling an undo
  stack for transactions (nice demo: reverse the last transaction).

Whichever you pick, implement it as its own module (e.g., `transaction/transaction_factory.py`),
write unit tests for it, and in your reflection cover:
- **Why** you chose it over the alternatives
- **Where** exactly it fits (which class/module it touches)
- **How** it improves flexibility, testability, or scalability — be concrete (e.g., "adding a
  new alert policy no longer requires editing `LowBalanceAlertObserver`'s code, just adding
  a new Strategy class").

---

## Step 7 — Dependency Injection Refactor

The rubric/instructions mention refactoring for DI to improve testability. Concretely for
this codebase:

- `LowBalanceAlertObserver(threshold)` already takes its dependency (the threshold) via
  the constructor rather than hardcoding it — that's DI. Keep this pattern.
- Consider: does `Balance` need to reach out to any concrete class directly (e.g., a
  hardcoded `print()` for alerts) instead of relying purely on injected observers? If so,
  refactor that call site to depend only on the `IBalanceObserver` interface.
- If you add a Strategy-based fourth pattern, injecting the strategy object into the
  constructor (rather than instantiating it internally) is exactly this principle applied
  again — good to call out explicitly in your reflection.

---

## Step 8 — Unit Tests

The starter already includes tests for Balance, Observer, Transaction, and the Adapter —
your job is to make them pass, plus add tests for your Step 6 pattern. Run:

```bash
cd starter
python3 -m unittest discover -v
```

All tests should pass with no errors before you submit. Since `Balance` is a Singleton,
double-check every test's `setUp()` calls `Balance.get_instance().reset()` (already done
in the given tests) so state doesn't leak between test cases.

---

## Step 9 — Reflection

Write `REFLECTION.md` (or add a section to `README.md`) covering:

1. **The four patterns used** — Singleton, Adapter, Observer, and your chosen fourth.
2. **How each improved the design** — one or two sentences per pattern, tied to *this*
   codebase (not generic textbook explanations).
3. **Trade-offs / challenges** — e.g., Singleton makes testing stateful (`reset()`
   everywhere), Observer adds indirection that can make control flow harder to trace,
   etc. Being honest about downsides is part of what's graded.

---

## Step 10 — Submission

- Clean up: make sure `python3 -m unittest discover -v` passes and `python3 main.py`
  runs without errors.
- Initialize git and push to your own GitHub repo (this folder currently isn't a git
  repo — `git clone` was blocked locally by an unaccepted Xcode license, so the files
  were downloaded as a zip instead; run `git init` here when you're ready).
- Include the reflection in the repo (README or separate file) and submit the repo link
  per the assignment instructions.

---

## Note on your local git setup

`git clone`/`git init` are currently blocked on this machine because Xcode's command-line
tools license hasn't been accepted. To fix that, run this in Terminal yourself (it needs
your password, so I can't run it for you):

```bash
sudo xcodebuild -license
```

After accepting, `git` will work normally for cloning, committing, and pushing this project.
