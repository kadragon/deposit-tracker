from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any
from src.services.split_service import SplitService


@dataclass(frozen=True)
class TransactionResult:
    success: bool
    amount_paid: Decimal
    deposit_used: Decimal
    cash_paid: Decimal


class TransactionService:
    def __init__(self, split_service: SplitService = None):
        self.split_service = split_service or SplitService()
    
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

    def handle_partial_payment_failures(self, receipt, use_deposit=False) -> Dict[Any, TransactionResult]:
        """Process split payment allowing partial failures without rollback."""
        user_amounts = self.split_service.split_receipt_by_user_assignment(receipt)
        
        results = {}
        
        for user, amount in user_amounts.items():
            if use_deposit:
                if user.deposit >= amount:
                    user.subtract_deposit(amount)
                    results[user] = TransactionResult(
                        success=True,
                        amount_paid=amount,
                        deposit_used=amount,
                        cash_paid=Decimal("0"),
                    )
                else:
                    # Insufficient deposit - mark as failed but continue with others
                    results[user] = TransactionResult(
                        success=False,
                        amount_paid=Decimal("0"),
                        deposit_used=Decimal("0"),
                        cash_paid=Decimal("0"),
                    )
            else:
                # Process with cash payment for each user
                results[user] = TransactionResult(
                    success=True,
                    amount_paid=amount,
                    deposit_used=Decimal("0"),
                    cash_paid=amount,
                )
        
        return results

    def rollback_on_insufficient_funds(self, receipt, use_deposit=False) -> Dict[Any, TransactionResult]:
        """Process split payment with all-or-nothing rollback on any insufficient funds."""
        user_amounts = self.split_service.split_receipt_by_user_assignment(receipt)
        
        if use_deposit:
            # First, check if all users have sufficient funds
            for user, amount in user_amounts.items():
                if user.deposit < amount:
                    # Insufficient funds detected - return all failures without any changes
                    return {
                        user: TransactionResult(
                            success=False,
                            amount_paid=Decimal("0"),
                            deposit_used=Decimal("0"),
                            cash_paid=Decimal("0"),
                        ) for user in user_amounts.keys()
                    }
            
            # All users have sufficient funds - process all payments
            results = {}
            for user, amount in user_amounts.items():
                user.subtract_deposit(amount)
                results[user] = TransactionResult(
                    success=True,
                    amount_paid=amount,
                    deposit_used=amount,
                    cash_paid=Decimal("0"),
                )
        else:
            # Cash payment - always successful
            results = {}
            for user, amount in user_amounts.items():
                results[user] = TransactionResult(
                    success=True,
                    amount_paid=amount,
                    deposit_used=Decimal("0"),
                    cash_paid=amount,
                )
        
        return results