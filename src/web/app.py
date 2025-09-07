from flask import Flask, request, redirect, url_for, abort, jsonify
from decimal import Decimal
from src.repositories.user_repository import UserRepository
from src.repositories.receipt_repository import ReceiptRepository
from src.repositories.coupon_repository import CouponRepository
from src.services.ocr_service import OCRService
from src.services.coupon_service import CouponService


def _get_value(source, key, default=''):
    """Gets a value from an object attribute or a dictionary key."""
    if hasattr(source, key):
        return getattr(source, key)
    if isinstance(source, dict):
        return source.get(key, default)
    return default


def _json_error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(
    user_repo=None,
    receipt_repo=None,
    coupon_repo=None,
    ocr_service=None,
    store_repo=None,
    coupon_service: CouponService | None = None,
) -> Flask:
    app = Flask(__name__)
    
    # Initialize dependencies with defaults if not provided
    if user_repo is None:
        user_repo = UserRepository()
    if receipt_repo is None:
        receipt_repo = ReceiptRepository()
    if coupon_repo is None:
        coupon_repo = CouponRepository()
    if ocr_service is None:
        ocr_service = OCRService()
    # store_repo and coupon_service are expected to be injected by caller/tests.
    # We avoid creating default Firestore-bound repos here to keep tests hermetic.
    if coupon_service is None and (coupon_repo is not None and store_repo is not None):
        coupon_service = CouponService(coupon_repo, store_repo)

    @app.route('/', methods=['GET', 'POST'])
    def user_selection():
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            if user_id:
                return redirect(url_for('dashboard', user_id=user_id))
            return 'No user selected', 400

        users = user_repo.list_all()

        result = 'user-selection'
        for user in users:
            result += str(_get_value(user, 'name'))

        return result

    @app.route('/dashboard/<user_id>')
    def dashboard(user_id):
        user = user_repo.get_by_id(user_id)
        if user is None:
            abort(404)

        receipts = receipt_repo.find_by_user_id(user_id)
        coupons = coupon_repo.get_by_user(user_id)

        result = f"{_get_value(user, 'name')}{_get_value(user, 'deposit')}"
        for receipt in receipts:
            store_name = _get_value(receipt, 'store_name')
            total_amount = _get_value(receipt, 'total_amount')
            result += f"{store_name}{total_amount}"
        for coupon in coupons:
            store_name = _get_value(coupon, 'store_name')
            count = _get_value(coupon, 'count')
            goal = _get_value(coupon, 'goal')
            result += f"{store_name}{count}{goal}"

        return result

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_form():
        if request.method == 'POST':
            if 'file' not in request.files:
                return _json_error('missing_file', 'No file', 400)

            file = request.files['file']
            if file.filename == '':
                return _json_error('no_file_selected', 'No file selected', 400)

            text = ocr_service.extract_text_from_image(file.read())
            store_name = ocr_service.parse_store_name(text)
            items = ocr_service.parse_items_and_prices(text)

            if not store_name:
                return _json_error('store_not_recognized', 'Store name not recognized', 400)
            if store_repo is None:
                return _json_error('store_repo_unavailable', 'Store repository unavailable', 500)

            # Find store by name to obtain canonical store_id
            store = store_repo.find_by_name(store_name)
            store_id = getattr(store, 'id', None)
            if not store_id:
                return _json_error('store_not_found', 'Store not found', 404)

            # Compute total from parsed items (fallback to 0)
            try:
                total_amount = sum(int(i.get('price', 0)) for i in items)
            except (ValueError, TypeError):
                total_amount = 0

            # Redirect to confirmation with canonical identifiers
            return redirect(url_for('confirm_receipt', store_id=store_id, total=str(total_amount)))

        return 'upload-form'

    @app.route('/confirm-receipt')
    def confirm_receipt():
        store_id = request.args.get('store_id', '')
        total = request.args.get('total', '')
        
        store_name = ''
        if store_repo and store_id:
            store = store_repo.get_by_id(store_id)
            # Sanitize store name to prevent XSS
            raw_store_name = _get_value(store, 'name')
            if raw_store_name:
                # Basic HTML escaping for XSS prevention
                store_name = str(raw_store_name).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
            else:
                store_name = ''
        
        users = user_repo.list_all()
        
        result = f'receipt-confirmation{store_name}{total}user-selection'
        for user in users:
            result += str(_get_value(user, 'name'))
        
        result += 'deposit-choice'
        
        return result

    @app.route('/process-receipt', methods=['POST'])
    def process_receipt():
        user_id = request.form.get('user_id')
        store_id = request.form.get('store_id')
        total = request.form.get('total')
        use_deposit = request.form.get('use_deposit')
        
        # Validate required fields
        if not user_id or not store_id or not total:
            return _json_error('missing_fields', 'Missing required fields', 400)
        
        # Normalize total as Decimal for consistency
        try:
            total_amount = Decimal(str(total))
            if total_amount <= 0:
                return _json_error('invalid_total', 'Invalid total amount', 400)
        except (ValueError, TypeError, Exception):
            return _json_error('invalid_total', 'Invalid total amount', 400)
        
        # Process transaction if using deposit
        if use_deposit == 'yes':
            user = user_repo.get_by_id(user_id)
            if not user:
                return _json_error('user_not_found', 'User not found', 404)
            # Ensure sufficient deposit; handle insufficiency gracefully
            if getattr(user, 'deposit', Decimal('0')) < total_amount:
                return _json_error('insufficient_deposit', 'Insufficient deposit', 400)
            user.subtract_deposit(total_amount)
            user_repo.save(user)
        
        # Award coupon for this purchase
        if coupon_service is not None:
            coupon_service.award_coupon_for_purchase(user_id, store_id)
        
        return redirect(url_for('success'))

    @app.route('/success')
    def success():
        return 'transaction-success'

    return app
