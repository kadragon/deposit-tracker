# Deposit Tracker

Simple receipt/ocr/coupon tracking project developed with TDD.

## Prerequisites

- Python `3.13` (managed via `uv`)
- `uv` package manager installed
- Optional: Google Cloud credentials for Vision/Firestore if running against real services

## Setup

- Create and activate virtual env (uv manages it automatically):
  - `uv run python --version`

- Install dependencies:
  - `uv sync`

## Running Tests

- Run all tests:
  - `uv run pytest -q`

- Run a specific test file:
  - `uv run pytest tests/services/test_ocr_service.py -q`

## Linting/Type Checking (optional)

No linter is configured. Type hints are present in core modules; you may use `pyright` or `mypy` if desired.

## Google Cloud Vision Integration

- `src/services/ocr_service.py` integrates with Vision in `extract_text()`.
- Tests mock `ImageAnnotatorClient` so no network is required for the suite.
- To use real OCR, set `GOOGLE_APPLICATION_CREDENTIALS` and pass an image path.

## Project Structure

- `src/models`: Domain models (`User`, `Store`, `Receipt`, `ReceiptItem`, `Coupon`)
- `src/repositories`: Firestore persistence facades
- `src/services`: OCR parsing and receipt processing services
- `tests`: TDD test suite

## Security (CSRF)

- Optional CSRF protection for modifying requests (POST/PUT/PATCH/DELETE).
- Enable with env var: `ENABLE_CSRF=1`.
- When enabled, include a CSRF token in either:
  - Header: `X-CSRF-Token: <token>`
  - Or form field: `csrf_token=<token>`
- Retrieve/generate token via: `GET /csrf-token` (returns `{ "csrf_token": "..." }`).

## API JSON Responses

- Certain admin endpoints support JSON responses via content negotiation without
  breaking existing behavior. To receive JSON:
  - Add query param: `?format=json`
  - And set header: `Accept: application/json`
- Supported endpoints:
  - `GET /admin/users/<user_id>/deposit-history`
  - `GET /admin/transactions`
  - `GET /admin/transactions/<receipt_id>/split-details`
  - `GET /admin/transactions/<receipt_id>/uploader-vs-payers`
  - `GET /admin/transactions/financial-report`

## Optional Batch Writes

- For bulk deposit operations, repositories may expose `save_many(users)`.
- Opt-in with env var: `ENABLE_BULK_SAVE=1` and implement `save_many` in your repo.
- Without this flag, the app saves each user individually for compatibility.
