# Repository Interfaces (Web Layer Expectations)

This document summarizes the methods the web layer (`src/web/app.py`) expects
from repository and service objects. Implementations may target Firestore or
in-memory fakes/mocks for tests.

## UserRepository

- `list_all() -> Iterable[User]`
- `get_by_id(user_id: str) -> Optional[User]`
- `save(user: User) -> None`
- `delete(user_id: str) -> None`
- `get_deposit_history(user_id: str) -> Iterable[DepositHistory]`
- Optional: `save_many(users: Iterable[User]) -> None` (batch write)

`User`
- Fields used: `name`, `deposit`
- Methods used: `add_deposit(amount: Decimal)`, `subtract_deposit(amount: Decimal)`

`DepositHistory`
- Fields used: `date: datetime`, `type: str`, `amount: Decimal`, `balance_after: Decimal`, `description: str`

## ReceiptRepository

- `list_all() -> Iterable[Receipt]`
- `find_by_user_id(user_id: str) -> Iterable[Receipt]`
- `find_by_store_name(store_name: str) -> Iterable[Receipt]`
- `find_by_date_range(start: datetime, end: datetime) -> Iterable[Receipt]`
- `get_by_id(receipt_id: str) -> Optional[Receipt]`
- `get_split_payment_details(receipt_id: str) -> Iterable[SplitDetail]`
- `get_payers_info(receipt_id: str) -> Iterable[dict]` (keys: `user_name`, `amount`)
- `generate_financial_report() -> dict`
  - Expected keys: `total_transactions`, `total_amount`, `deposit_payments`, `cash_payments`,
    `by_user` (list of `{user_name, total_spent, deposit_used}`),
    `by_store` (list of `{store_name, total_amount, transaction_count}`)

`Receipt`
- Fields used: `id`, `user_name`, `store_name`, `total_amount`, `date`, `is_split_payment`

`SplitDetail`
- Fields used: `user_name`, `amount`, `payment_method`

## StoreRepository

- `list_all() -> Iterable[Store]`
- `get_by_id(store_id: str) -> Optional[Store]`
- `find_by_name(name: str) -> Optional[Store]`
- `save(store: Store) -> None`
- Optional: `update(store_id: str, changes: dict) -> None`

`Store`
- Fields used: `name`, `coupon_enabled`, `coupon_goal`
- Methods used: `set_coupon_goal(goal: int)`

## CouponRepository

- `get_by_user(user_id: str) -> Iterable[Coupon]`

`Coupon`
- Fields used: `store_name`, `count`, `goal`

## CouponService

- `award_coupon_for_purchase(user_id: str, store_id: str) -> None`

