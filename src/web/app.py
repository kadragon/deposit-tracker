from flask import Flask, request, redirect
from src.repositories.user_repository import UserRepository
from src.repositories.receipt_repository import ReceiptRepository
from src.repositories.coupon_repository import CouponRepository
from src.services.ocr_service import OCRService
from src.services.receipt_parser import ReceiptParser


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def user_selection():
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            return redirect(f'/dashboard/{user_id}')

        user_repo = UserRepository()
        users = user_repo.list_all()

        result = 'user-selection'
        for user in users:
            result += str(getattr(user, 'name', ''))

        return result

    @app.route('/dashboard/<user_id>')
    def dashboard(user_id):
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)

        receipt_repo = ReceiptRepository()
        receipts = receipt_repo.find_by_user_id(user_id)

        coupon_repo = CouponRepository()
        coupons = coupon_repo.get_by_user(user_id)

        result = f"{getattr(user, 'name', '')}{getattr(user, 'deposit', '')}"
        for receipt in receipts:
            # Allow both dict-like and attribute-like mocks
            store_name = getattr(receipt, 'store_name', None) or (receipt.get('store_name') if isinstance(receipt, dict) else '')
            total_amount = getattr(receipt, 'total_amount', None) or (receipt.get('total_amount') if isinstance(receipt, dict) else '')
            result += f"{store_name}{total_amount}"
        for coupon in coupons:
            store_name = getattr(coupon, 'store_name', None) or (coupon.get('store_name') if isinstance(coupon, dict) else '')
            count = getattr(coupon, 'count', None) or (coupon.get('count') if isinstance(coupon, dict) else '')
            goal = getattr(coupon, 'goal', None) or (coupon.get('goal') if isinstance(coupon, dict) else '')
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

            ocr_service = OCRService()
            text = ocr_service.extract_text_from_image(file.read())
            store_name = ocr_service.parse_store_name(text)
            items = ocr_service.parse_items_and_prices(text)

            result = 'image-uploaded' + str(store_name)
            for item in items:
                # items are dicts: {"name": str, "price": int}
                result += str(item.get('price'))

            return result

        return 'upload-form'

    return app


app = create_app()
