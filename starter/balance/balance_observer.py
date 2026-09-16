# balance_observer.py

class IBalanceObserver:
    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    def update(self, balance, transaction):
        """Print balance update message."""
        print(
            f"[Balance Update] Applied {transaction} -> "
            f"New balance: ${balance:.2f}"
        )


class LowBalanceAlertObserver(IBalanceObserver):
    def __init__(self, threshold):
        self.threshold = threshold
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
        if self.alert_triggered:
            print(
                f"[ALERT] Balance ${balance:.2f} is below threshold "
                f"of ${self.threshold:.2f}!"
            )
