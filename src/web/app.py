from flask import Flask, request, redirect, url_for, abort
from src.repositories.user_repository import UserRepository
from src.repositories.receipt_repository import ReceiptRepository
from src.repositories.coupon_repository import CouponRepository
from src.repositories.store_repository import StoreRepository
from src.services.ocr_service import OCRService
from src.services.coupon_service import CouponService


def _get_value(source, key, default=''):
    """Gets a value from an object attribute or a dictionary key."""
    if hasattr(source, key):
        return getattr(source, key)
    if isinstance(source, dict):
        return source.get(key, default)
    return default


def create_app(user_repo=None, receipt_repo=None, coupon_repo=None, ocr_service=None) -> Flask:
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
                return 'No file'

            file = request.files['file']
            if file.filename == '':
                return 'No file selected'

            text = ocr_service.extract_text_from_image(file.read())
            store_name = ocr_service.parse_store_name(text)
            items = ocr_service.parse_items_and_prices(text)

            result = 'image-uploaded' + str(store_name)
            for item in items:
                # items are dicts: {"name": str, "price": int}
                result += str(item.get('price'))

            return result

        return 'upload-form'

    @app.route('/confirm-receipt')
    def confirm_receipt():
        store_name = request.args.get('store_name', '')
        total = request.args.get('total', '')
        items = request.args.get('items', '')
        
        users = user_repo.list_all()
        
        result = f'receipt-confirmation{store_name}{total}user-selection'
        for user in users:
            result += str(_get_value(user, 'name'))
        
        result += 'deposit-choice'
        
        return result

    @app.route('/process-receipt', methods=['POST'])
    def process_receipt():
        user_id = request.form.get('user_id')
        store_name = request.form.get('store_name')
        total = request.form.get('total')
        use_deposit = request.form.get('use_deposit')
        
        # Process transaction if using deposit
        if use_deposit == 'yes' and user_id and total:
            user = user_repo.get_by_id(user_id)
            if user:
                user.subtract_deposit(int(total))
                user_repo.save(user)
        
        # Award coupon for this purchase
        if user_id and store_name:
            store_repo = StoreRepository()
            coupon_service = CouponService(coupon_repo, store_repo)
            coupon_service.award_coupon(user_id, store_name)
        
        return redirect(url_for('success'))

    @app.route('/success')
    def success():
        return 'transaction-success'

    return app


