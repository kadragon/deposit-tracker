from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TransactionResult:
    success: bool
    amount_paid: int
    deposit_used: int
    cash_paid: int


class TransactionService:
    def process_transaction(self, receipt, use_deposit=False):
        total_amount: Decimal = receipt.calculate_total()
        
        if use_deposit:
            if receipt.user.deposit >= total_amount:
                # Keep User.deposit as int to avoid ripple effects
                receipt.user.subtract_deposit(int(total_amount))
                return TransactionResult(
                    success=True,
                    amount_paid=int(total_amount),
                    deposit_used=int(total_amount),
                    cash_paid=0,
                )
        else:
            # Process transaction without deposit (cash payment)
            return TransactionResult(
                success=True,
                amount_paid=int(total_amount),
                deposit_used=0,
                cash_paid=int(total_amount),
            )
        
        return TransactionResult(
            success=False,
            amount_paid=0,
            deposit_used=0,
            cash_paid=0
        )
