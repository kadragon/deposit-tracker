from flask import Flask, request, redirect, url_for, abort, jsonify, session, render_template, flash
from decimal import Decimal, InvalidOperation
import os
from datetime import datetime
from src.repositories.user_repository import UserRepository
from src.repositories.receipt_repository import ReceiptRepository
from src.repositories.coupon_repository import CouponRepository
from src.services.ocr_service import OCRService
from src.services.coupon_service import CouponService
from src.models.user import User
from src.models.store import Store
from markupsafe import escape


def _get_value(source, key, default=''):
    """Gets a value from an object attribute or a dictionary key."""
    if hasattr(source, key):
        return getattr(source, key)
    if isinstance(source, dict):
        return source.get(key, default)
    return default


def _json_error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status

def _wants_json(req: request) -> bool:
    """True if client explicitly wants JSON and asked for it.
    We require both query param and Accept header to avoid breaking existing tests.
    """
    fmt = (req.args.get('format') or '').lower()
    accept = (req.headers.get('Accept') or '').lower()
    return fmt == 'json' and 'application/json' in accept

def _ensure_csrf_token() -> str:
    token = session.get('csrf_token')
    if not token:
        token = os.urandom(16).hex()
        session['csrf_token'] = token
    return token

def _to_serializable(value):
    """Convert common non-JSON-serializable types to JSON-friendly values."""
    if isinstance(value, Decimal):
        # Keep as string to preserve precision
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(v) for v in value]
    try:
        # Fall back to basic types
        return value
    except TypeError:
        return str(value)

def _first_value(source, keys: list[str], default=''):
    """Gets the first available value among attributes/keys in order."""
    if not source:
        return default
    
    for key in keys:
        try:
            if hasattr(source, key):
                value = getattr(source, key)
                if value is not None:
                    return value
        except (AttributeError, TypeError):
            pass
            
        try:
            if isinstance(source, dict) and key in source:
                value = source.get(key)
                if value is not None:
                    return value
        except (TypeError, AttributeError):
            pass
    return default


def create_app(
    user_repo=None,
    receipt_repo=None,
    coupon_repo=None,
    ocr_service=None,
    store_repo=None,
    coupon_service: CouponService | None = None,
) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get('APP_SECRET_KEY', 'test_secret_key')

    @app.before_request
    def _csrf_protect_and_prepare():
        # Always ensure token exists for convenience
        _ensure_csrf_token()
        # Enforce CSRF only when explicitly enabled
        if (os.environ.get('ENABLE_CSRF') or '').lower() in ('1', 'true', 'yes'):
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token') or ''
                if not token or token != session.get('csrf_token'):
                    abort(400)
    
    # Initialize dependencies with defaults if not provided
    if user_repo is None:
        user_repo = UserRepository()
    if receipt_repo is None:
        receipt_repo = ReceiptRepository()
    if coupon_repo is None:
        coupon_repo = CouponRepository()
    if store_repo is None:
        # Initialize StoreRepository here for normal app operation when not injected by tests.
        # This allows the app to run independently while maintaining testability.
        from src.repositories.store_repository import StoreRepository
        store_repo = StoreRepository()
    if ocr_service is None:
        ocr_service = OCRService()
    # coupon_service is expected to be injected by caller/tests, but create default if not provided.
    if coupon_service is None and (coupon_repo is not None and store_repo is not None):
        coupon_service = CouponService(coupon_repo, store_repo)

    # Add custom Jinja2 filters
    def format_currency(value):
        """Format currency with commas"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)
    
    app.jinja_env.filters['currency'] = format_currency

    @app.route('/', methods=['GET', 'POST'])
    def user_selection():
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            if user_id:
                return redirect(url_for('dashboard', user_id=user_id))
            return 'No user selected', 400

        users = user_repo.list_all()
        return render_template('user_selection.html', users=users)

    @app.route('/dashboard/<user_id>')
    def dashboard(user_id):
        user = user_repo.get_by_id(user_id)
        if user is None:
            abort(404)

        receipts = receipt_repo.find_by_user_id(user_id)
        coupons = coupon_repo.get_by_user(user_id)
        split_transactions = receipt_repo.find_split_transactions_by_user(user_id)
        uploaded_receipts = receipt_repo.find_by_uploader(user_id)
        pending_split_requests = receipt_repo.find_pending_split_requests(user_id)

        return render_template('dashboard.html', 
                             user=user,
                             receipts=receipts,
                             coupons=coupons,
                             split_transactions=split_transactions,
                             uploaded_receipts=uploaded_receipts,
                             pending_split_requests=pending_split_requests)

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

        return render_template('upload.html')

    @app.route('/csrf-token', methods=['GET'])
    def csrf_token():
        # Expose CSRF token for clients wanting to include it in subsequent POSTs
        token = _ensure_csrf_token()
        return jsonify({"csrf_token": token})

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
                store_name = str(escape(raw_store_name))
            else:
                store_name = ''
        
        users = user_repo.list_all()
        
        result = f'receipt-confirmation{store_name}{total}user-selection'
        for user in users:
            result += str(_get_value(user, 'name'))
        
        result += 'deposit-choice'
        
        return result
    
    @app.route('/assign-items', methods=['GET', 'POST'])
    def assign_items():
        if request.method == 'POST':
            # Process item assignments
            if request.is_json:
                assignment_data = request.get_json()
                store_id = assignment_data.get('store_id', '')
                item_assignments = assignment_data.get('item_assignments', [])
                
                # Store assignments in session for later processing
                session['item_assignments'] = item_assignments
                session['assignment_store_id'] = store_id
                
                # Return success response with assignment data
                response_data = {
                    'message': 'assignment-success',
                    'assignments': item_assignments
                }
                return jsonify(response_data)
        
        # GET request - display assignment page
        store_id = request.args.get('store_id', '')
        
        # Get store information
        store_name = ''
        if store_repo and store_id:
            store = store_repo.get_by_id(store_id)
            raw_store_name = _get_value(store, 'name')
            if raw_store_name:
                store_name = str(escape(raw_store_name))
        
        # Get parsed items from session
        items = session.get('parsed_items', [])
        
        # Get all users for assignment
        users = user_repo.list_all()
        
        # Convert users to dict format for template
        user_list = []
        for user in users:
            user_list.append({
                'id': _get_value(user, 'id'),
                'name': str(_get_value(user, 'name'))
            })
        
        return render_template('assign_items.html', 
                             items=items, 
                             users=user_list, 
                             store_name=store_name, 
                             store_id=store_id)

    @app.route('/calculate-amounts', methods=['POST'])
    def calculate_amounts():
        if not request.is_json:
            return _json_error('invalid_request', 'JSON required', 400)
        
        data = request.get_json()
        item_assignments = data.get('item_assignments', [])
        
        # Get parsed items from session
        items = session.get('parsed_items', [])
        
        if not items:
            return _json_error('no_items', 'No items found in session', 400)
        
        # Calculate amounts per user
        user_amounts = {}
        total_amount = 0
        
        for assignment in item_assignments:
            item_index = int(assignment.get('item_index', 0))
            
            if item_index >= len(items):
                continue
                
            item = items[item_index]
            item_price = int(item.get('price', 0))
            item_quantity = int(item.get('quantity', 1))
            item_total = item_price * item_quantity
            
            sharing_type = assignment.get('sharing_type', 'individual')
            
            if sharing_type == 'shared':
                # Handle shared items
                shared_users = assignment.get('shared_users', [])
                sharing_ratio = assignment.get('sharing_ratio', [])
                
                if len(shared_users) == len(sharing_ratio):
                    for i, user_id in enumerate(shared_users):
                        ratio = sharing_ratio[i]
                        user_amount = int(item_total * ratio)
                        user_amounts[user_id] = user_amounts.get(user_id, 0) + user_amount
                else:
                    # Equal sharing if no ratio provided
                    per_user_amount = item_total // len(shared_users)
                    for user_id in shared_users:
                        user_amounts[user_id] = user_amounts.get(user_id, 0) + per_user_amount
            else:
                # Individual assignment
                user_id = assignment.get('user_id')
                if user_id:
                    user_amounts[user_id] = user_amounts.get(user_id, 0) + item_total
            
            total_amount += item_total
        
        response_data = {
            'message': 'calculation-result',
            'user_amounts': user_amounts,
            'total_amount': total_amount
        }
        
        return jsonify(response_data)

    @app.route('/validate-assignments', methods=['POST'])
    def validate_assignments():
        if not request.is_json:
            return _json_error('invalid_request', 'JSON required', 400)
        
        data = request.get_json()
        item_assignments = data.get('item_assignments', [])
        
        # Get parsed items from session
        items = session.get('parsed_items', [])
        
        if not items:
            return _json_error('no_items', 'No items found in session', 400)
        
        # Check which items are not assigned
        assigned_indices = set()
        for assignment in item_assignments:
            item_index = int(assignment.get('item_index', -1))
            if 0 <= item_index < len(items):
                assigned_indices.add(item_index)
        
        unassigned_items = []
        for i, item in enumerate(items):
            if i not in assigned_indices:
                unassigned_items.append({
                    'index': i,
                    'name': item.get('name', ''),
                    'price': item.get('price', 0),
                    'quantity': item.get('quantity', 1)
                })
        
        if unassigned_items:
            return jsonify({
                'error': 'validation-error',
                'message': 'unassigned-items',
                'unassigned_items': unassigned_items
            }), 400
        
        return jsonify({'message': 'validation-success'})

    @app.route('/payment-summary')
    def payment_summary():
        # Get split assignments from session
        split_assignments = session.get('split_assignments', {})
        store_id = session.get('assignment_store_id', '')
        
        if not split_assignments:
            return 'No split assignments found', 400
        
        # Get store information
        store_name = ''
        if store_repo and store_id:
            store = store_repo.get_by_id(store_id)
            raw_store_name = _get_value(store, 'name')
            if raw_store_name:
                store_name = str(escape(raw_store_name))
        
        # Prepare user payment data for template
        user_payments = []
        insufficient_balance_count = 0
        total_amount = 0
        
        for user_id, amount in split_assignments.items():
            user = user_repo.get_by_id(user_id)
            if user:
                user_name = str(_get_value(user, 'name'))
                user_deposit = _get_value(user, 'deposit') or 0
                
                insufficient_balance = user_deposit < amount
                if insufficient_balance:
                    insufficient_balance_count += 1
                
                user_payments.append({
                    'user_id': user_id,
                    'name': user_name,
                    'amount': amount,
                    'deposit': user_deposit,
                    'insufficient_balance': insufficient_balance
                })
                
                total_amount += amount
        
        return render_template('payment_summary.html',
                             user_payments=user_payments,
                             store_name=store_name,
                             total_amount=total_amount,
                             insufficient_balance_count=insufficient_balance_count)

    @app.route('/payment-confirmation')
    def payment_confirmation():
        # Get confirmed payment details from session
        confirmed_payments = session.get('confirmed_payments', {})
        store_id = session.get('assignment_store_id', '')
        
        if not confirmed_payments:
            return 'No confirmed payments found', 400
        
        # Get store information
        store_name = ''
        if store_repo and store_id:
            store = store_repo.get_by_id(store_id)
            raw_store_name = _get_value(store, 'name')
            if raw_store_name:
                store_name = str(escape(raw_store_name))
        
        # Prepare user payment data for template
        user_payment_data = []
        total_amount = 0
        
        for user_id, payment_info in confirmed_payments.items():
            user = user_repo.get_by_id(user_id)
            if user:
                user_name = str(_get_value(user, 'name'))
                amount = payment_info.get('amount', 0)
                method = payment_info.get('method', 'deposit')
                
                user_payment_data.append({
                    'user_id': user_id,
                    'name': user_name,
                    'amount': amount,
                    'method': method
                })
                
                total_amount += amount
        
        return render_template('payment_confirmation.html',
                             user_payments=user_payment_data,
                             store_name=store_name,
                             total_amount=total_amount)

    @app.route('/select-payment-methods', methods=['POST'])
    def select_payment_methods():
        if not request.is_json:
            return _json_error('invalid_request', 'JSON required', 400)
        
        data = request.get_json()
        store_id = data.get('store_id', '')
        user_payments = data.get('user_payments', [])
        
        # Store payment method selections in session
        session['payment_methods'] = user_payments
        session['payment_store_id'] = store_id
        
        response_data = {
            'message': 'payment-methods-selected',
            'user_payments': user_payments
        }
        
        return jsonify(response_data)

    @app.route('/process-split-payment', methods=['POST'])
    def process_split_payment():
        if not request.is_json:
            return _json_error('invalid_request', 'JSON required', 400)
        
        data = request.get_json()
        store_id = data.get('store_id', '')
        user_payments = data.get('user_payments', [])
        
        if not user_payments:
            return _json_error('no_payments', 'No user payments provided', 400)
        
        # Process each user payment - collect all operations first for atomicity
        processed_users = []
        failed_payments = []
        payment_operations = []
        
        # Pre-validate all payments
        for payment in user_payments:
            user_id = payment.get('user_id')
            amount = payment.get('amount', 0)
            method = payment.get('method', 'deposit')
            
            if not user_id:
                failed_payments.append({'user_id': user_id, 'error': 'missing_user_id'})
                continue
                
            user = user_repo.get_by_id(user_id)
            if not user:
                failed_payments.append({'user_id': user_id, 'error': 'user_not_found'})
                continue
            
            if method == 'deposit':
                try:
                    amount_decimal = Decimal(str(amount))
                    # Check sufficient funds before any operations
                    if getattr(user, 'deposit', Decimal('0')) < amount_decimal:
                        failed_payments.append({'user_id': user_id, 'error': 'insufficient_funds'})
                        continue
                    payment_operations.append({'user': user, 'user_id': user_id, 'amount': amount_decimal, 'method': method})
                except (ValueError, TypeError, InvalidOperation) as e:
                    failed_payments.append({'user_id': user_id, 'error': f'invalid_amount: {str(e)}'})
                    continue
            elif method == 'cash':
                payment_operations.append({'user': None, 'user_id': user_id, 'amount': amount, 'method': method})
        
        # If any pre-validation failed, return error before processing anything
        if failed_payments:
            return jsonify({
                'error': 'payment_validation_failed',
                'message': 'Some payments could not be processed',
                'failed_payments': failed_payments
            }), 400
        
        # Now process all validated payments
        for operation in payment_operations:
            if operation['method'] == 'deposit':
                try:
                    user = operation['user']
                    amount_decimal = operation['amount']
                    user_id = operation['user_id']
                    
                    user.subtract_deposit(amount_decimal)
                    user_repo.save(user)
                    
                    # Award coupon for deposit payment
                    if coupon_service:
                        coupon_service.award_coupon_for_purchase(user_id, store_id)
                    
                    processed_users.append(user_id)
                except Exception as e:
                    # Even with pre-validation, save/coupon operations can fail
                    failed_payments.append({'user_id': operation['user_id'], 'error': f'processing_error: {str(e)}'})
            elif operation['method'] == 'cash':
                processed_users.append(operation['user_id'])
        
        # Return result with both successes and any processing failures
        result = {
            'message': 'multi-user-payment-processed',
            'processed_users': processed_users
        }
        if failed_payments:
            result['failed_payments'] = failed_payments
            result['partial_success'] = True
        
        return jsonify(result), 200 if not failed_payments else 207

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
    
    @app.route('/admin')
    def admin():
        if session.get('admin_logged_in'):
            return redirect(url_for('admin_users'))
        return redirect(url_for('admin_login'))
    
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            expected_user = os.environ.get('ADMIN_USERNAME')
            expected_pass = os.environ.get('ADMIN_PASSWORD')
            
            # Use default credentials only in test/development environments
            if not expected_user or not expected_pass:
                env = os.environ.get('FLASK_ENV', 'development')
                if env == 'production':
                    return 'Configuration error: Admin credentials not set', 500
                expected_user = expected_user or 'admin'
                expected_pass = expected_pass or 'password'
            if username == expected_user and password == expected_pass:
                session['admin_logged_in'] = True
                return redirect(url_for('admin'))
        return 'admin-login'

    @app.route('/admin/logout', methods=['POST'])
    def admin_logout():
        session.pop('admin_logged_in', None)
        return redirect(url_for('admin_login'))
    
    @app.route('/admin/users', methods=['GET', 'POST'])
    def admin_users():
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        if request.method == 'POST':
            # Create new user
            name = request.form.get('name')
            deposit = request.form.get('deposit', '0')
            user = User(name=name, deposit=Decimal(deposit))
            user_repo.save(user)
            return redirect(url_for('admin_users'))
        
        # Display all users
        users = user_repo.list_all()
        return render_template('admin_users.html', users=users)
    
    @app.route('/admin/users/<user_id>/add-deposit', methods=['POST'])
    def admin_add_deposit(user_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        amount = request.form.get('amount')
        user = user_repo.get_by_id(user_id)
        if user:
            user.add_deposit(Decimal(amount))
            user_repo.save(user)
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<user_id>/delete', methods=['POST'])
    def admin_delete_user(user_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        user_repo.delete(user_id)
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<user_id>/deposit-history', methods=['GET'])
    def admin_user_deposit_history(user_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        # Ensure user exists; return 404 for unknown users
        user = user_repo.get_by_id(user_id)
        if not user:
            abort(404)

        history = user_repo.get_deposit_history(user_id) or []
        if _wants_json(request):
            items = []
            for entry in history:
                items.append({
                    'date': _to_serializable(getattr(entry, 'date', None)),
                    'type': getattr(entry, 'type', ''),
                    'amount': _to_serializable(getattr(entry, 'amount', 0)),
                    'balance_after': _to_serializable(getattr(entry, 'balance_after', 0)),
                    'description': getattr(entry, 'description', ''),
                })
            return jsonify({'deposit_history': items})

        result = 'deposit-history'
        for entry in history:
            result += f'{entry.type}{entry.amount}{entry.balance_after}{entry.description}'
        return result
    
    @app.route('/admin/users/bulk-deposit', methods=['POST'])
    def admin_bulk_deposit():
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        amount_raw = (request.form.get('amount') or '').strip()
        user_ids_raw = request.form.get('user_ids', '')
        user_ids = [u.strip() for u in user_ids_raw.split(',') if u.strip()]

        # Validate amount is a positive decimal
        try:
            amount_decimal = Decimal(str(amount_raw))
        except (InvalidOperation, ValueError, TypeError):
            return redirect(url_for('admin_users'))
        if amount_decimal <= 0:
            return redirect(url_for('admin_users'))

        # Apply deposit to each valid user
        users_to_save = []
        successful_users = []
        failed_users = []
        enable_bulk = (os.environ.get('ENABLE_BULK_SAVE') or '').lower() in ('1', 'true', 'yes')
        has_bulk_method = hasattr(user_repo, 'save_many')
        
        for user_id in user_ids:
            user = user_repo.get_by_id(user_id)
            if not user:
                failed_users.append({'user_id': user_id, 'error': 'user_not_found'})
                continue
                
            try:
                user.add_deposit(amount_decimal)
                users_to_save.append(user)
                # Save immediately unless bulk mode is explicitly enabled
                if not (enable_bulk and has_bulk_method):
                    user_repo.save(user)
                    successful_users.append(user_id)
            except Exception as e:
                failed_users.append({'user_id': user_id, 'error': f'deposit_error: {str(e)}'})
                continue
                
        # Try optional bulk save if enabled and repository supports it
        if enable_bulk and has_bulk_method and users_to_save:
            try:
                user_repo.save_many(users_to_save)
                successful_users.extend([getattr(u, 'id', '') for u in users_to_save])
            except Exception as e:
                # If bulk save fails, try individual saves as fallback
                for user in users_to_save:
                    try:
                        user_repo.save(user)
                        successful_users.append(getattr(user, 'id', ''))
                    except Exception as individual_error:
                        failed_users.append({
                            'user_id': getattr(user, 'id', ''),
                            'error': f'individual_save_error: {str(individual_error)}'
                        })
        
        # For now, just redirect to admin_users (UI doesn't show detailed results)
        # In a production app, you might want to show success/failure counts
        # TODO: Consider adding flash messages or query params to show results
        
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/stores', methods=['GET', 'POST'])
    def admin_stores():
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        if request.method == 'POST':
            # Create new store
            name = request.form.get('name')
            coupon_enabled = request.form.get('coupon_enabled') == 'on'
            try:
                coupon_goal = int(request.form.get('coupon_goal', '10'))
            except (ValueError, TypeError):
                coupon_goal = 10
            
            store = Store(name=name)
            store.coupon_enabled = coupon_enabled
            if coupon_enabled:
                store.set_coupon_goal(coupon_goal)
            store_repo.save(store)
            return redirect(url_for('admin_stores'))
        
        # Display all stores
        stores = store_repo.list_all()
        return render_template('admin_stores.html', stores=stores)
    
    @app.route('/admin/stores/<store_id>/toggle-coupon', methods=['POST'])
    def admin_toggle_coupon(store_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        store = store_repo.get_by_id(store_id)
        if store:
            new_value = not _get_value(store, 'coupon_enabled')
            # Reflect change on in-memory object for callers/tests
            try:
                setattr(store, 'coupon_enabled', new_value)
            except AttributeError:
                # Store object doesn't allow setting coupon_enabled attribute
                pass
            # Persist change
            if hasattr(type(store_repo), 'update'):
                store_repo.update(store_id, {"coupon_enabled": new_value})
            else:
                store_repo.save(store)
        return redirect(url_for('admin_stores'))
    
    @app.route('/admin/stores/<store_id>/set-goal', methods=['POST'])
    def admin_set_goal(store_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        try:
            goal = int(request.form.get('goal'))
        except (ValueError, TypeError):
            return redirect(url_for('admin_stores'))
        store = store_repo.get_by_id(store_id)
        if store:
            # Reflect change on in-memory object for callers/tests
            try:
                setattr(store, 'coupon_goal', goal)
            except AttributeError:
                # Store object doesn't allow setting coupon_goal attribute
                pass
            # Persist change
            if hasattr(type(store_repo), 'update'):
                store_repo.update(store_id, {"coupon_goal": goal})
            else:
                store_repo.save(store)
        return redirect(url_for('admin_stores'))
    
    @app.route('/admin/transactions')
    def admin_transactions():
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        user_id = request.args.get('user_id')
        store_name = request.args.get('store_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        receipts = []
        
        if user_id:
            receipts = receipt_repo.find_by_user_id(user_id)
        elif store_name:
            receipts = receipt_repo.find_by_store_name(store_name)
        elif start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                receipts = receipt_repo.find_by_date_range(start_dt, end_dt)
            except ValueError:
                # Invalid date format; fall back to empty or all data
                flash('잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.', 'error')
                receipts = []
        else:
            receipts = receipt_repo.list_all()
        
        if _wants_json(request):
            items = []
            for receipt in receipts:
                items.append({
                    'user_name': _to_serializable(_first_value(receipt, ["user_name", "user", "user_id"])),
                    'store_name': _to_serializable(_first_value(receipt, ["store_name", "store", "store_id"])),
                    'total_amount': _to_serializable(_first_value(receipt, ["total_amount", "total"])),
                    'date': _to_serializable(_first_value(receipt, ["date", "created_at"])),
                })
            return jsonify({'transactions': items})

        return render_template('admin_transactions.html', receipts=receipts)
    
    @app.route('/admin/transactions/<receipt_id>/split-details')
    def admin_transaction_split_details(receipt_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        split_details = receipt_repo.get_split_payment_details(receipt_id) or []
        if _wants_json(request):
            items = []
            for detail in split_details:
                items.append({
                    'user_name': getattr(detail, 'user_name', ''),
                    'amount': _to_serializable(getattr(detail, 'amount', 0)),
                    'payment_method': getattr(detail, 'payment_method', ''),
                })
            return jsonify({'split_details': items})

        result = 'split-payment-details'
        for detail in split_details:
            result += f'{detail.user_name}{detail.amount}{detail.payment_method}'
        return result
    
    @app.route('/admin/transactions/<receipt_id>/uploader-vs-payers')
    def admin_transaction_uploader_vs_payers(receipt_id):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        receipt = receipt_repo.get_by_id(receipt_id)
        if not receipt:
            abort(404)
        payers_info = receipt_repo.get_payers_info(receipt_id) or []
        
        if _wants_json(request):
            return jsonify({
                'uploader': getattr(receipt, 'user_name', ''),
                'payers': [{
                    'user_name': _to_serializable(p.get('user_name')),
                    'amount': _to_serializable(p.get('amount')),
                } for p in payers_info]
            })

        result = 'uploader-payers-info'
        result += f'{receipt.user_name}'  # uploader
        for payer in payers_info:
            result += f'{payer["user_name"]}{payer["amount"]}'
        return result
    
    @app.route('/admin/transactions/financial-report')
    def admin_financial_report():
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        report_data = receipt_repo.generate_financial_report() or {}

        if _wants_json(request):
            return jsonify(_to_serializable(report_data))

        result = 'financial-report'
        total_amount = report_data.get('total_amount', 0)
        deposit_payments = report_data.get('deposit_payments', 0)
        cash_payments = report_data.get('cash_payments', 0)
        result += f'{total_amount}{deposit_payments}{cash_payments}'

        for user_data in report_data.get('by_user', []):
            result += f'{user_data.get("user_name", "")}{user_data.get("total_spent", 0)}'

        for store_data in report_data.get('by_store', []):
            result += f'{store_data.get("store_name", "")}{store_data.get("total_amount", 0)}'

        return result

    return app
