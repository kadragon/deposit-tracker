from flask import Flask, request, redirect
from src.repositories.user_repository import UserRepository
from src.repositories.receipt_repository import ReceiptRepository
from src.repositories.coupon_repository import CouponRepository
from src.services.ocr_service import OCRService
from src.services.receipt_parser import ReceiptParser

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def user_selection():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        return redirect(f'/dashboard/{user_id}')
    
    user_repo = UserRepository()
    users = user_repo.get_all()
    
    result = 'user-selection'
    for user in users:
        result += str(user.name)
    
    return result


@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    user_repo = UserRepository()
    user = user_repo.get_by_id(user_id)
    
    receipt_repo = ReceiptRepository()
    receipts = receipt_repo.get_by_user_id(user_id)
    
    coupon_repo = CouponRepository()
    coupons = coupon_repo.get_by_user_id(user_id)
    
    result = str(user.name) + str(user.deposit)
    for receipt in receipts:
        result += str(receipt.store_name) + str(receipt.total_amount)
    for coupon in coupons:
        result += str(coupon.store_name) + str(coupon.count) + str(coupon.goal)
    
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
        for item_name, price in items:
            result += str(price)
        
        return result
    
    return 'upload-form'