class TransactionResult:
    def __init__(self, success, amount_paid, deposit_used, cash_paid):
        self.success = success
        self.amount_paid = amount_paid
        self.deposit_used = deposit_used
        self.cash_paid = cash_paid


class TransactionService:
    def process_transaction(self, receipt, use_deposit=False):
        total_amount = receipt.calculate_total()
        
        if use_deposit:
            if receipt.user.deposit >= total_amount:
                receipt.user.subtract_deposit(total_amount)
                return TransactionResult(
                    success=True,
                    amount_paid=total_amount,
                    deposit_used=total_amount,
                    cash_paid=0
                )
        else:
            # Process transaction without deposit (cash payment)
            return TransactionResult(
                success=True,
                amount_paid=total_amount,
                deposit_used=0,
                cash_paid=total_amount
            )
        
        return TransactionResult(
            success=False,
            amount_paid=0,
            deposit_used=0,
            cash_paid=0
        )