from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TransactionResult:
    success: bool
    amount_paid: Decimal
    deposit_used: Decimal
    cash_paid: Decimal


class TransactionService:
    def process_transaction(self, receipt, use_deposit=False):
        total_amount: Decimal = receipt.calculate_total()
        
        if use_deposit:
            if receipt.user.deposit >= total_amount:
                # This assumes subtract_deposit can handle Decimal.
                receipt.user.subtract_deposit(total_amount)
                return TransactionResult(
                    success=True,
                    amount_paid=total_amount,
                    deposit_used=total_amount,
                    cash_paid=Decimal("0"),
                )
            else:
                # Insufficient deposit, transaction fails.
                return TransactionResult(
                    success=False,
                    amount_paid=Decimal("0"),
                    deposit_used=Decimal("0"),
                    cash_paid=Decimal("0"),
                )
        else:
            # Process transaction without deposit (cash payment).
            return TransactionResult(
                success=True,
                amount_paid=total_amount,
                deposit_used=Decimal("0"),
                cash_paid=total_amount,
            )
