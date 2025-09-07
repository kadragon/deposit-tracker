# 영수증 기반 예치금 관리 시스템 - TDD 개발 계획

## 개발 접근 방식
- Kent Beck의 TDD 원칙 준수: Red → Green → Refactor
- 각 기능을 작은 단위로 분해하여 테스트 우선 개발
- Tidy First 원칙: 구조적 변경과 동작적 변경을 분리

## 기술 스택
- **패키지 관리**: uv (fast Python package installer and resolver)
- **라이브러리 참조**: Context7 MCP를 통한 최신 라이브러리 문서 확인
- Backend: Python (Flask + functions-framework)
- Database: Firestore
- Frontend: Jinja2 + TailwindCSS(DaisyUI) + HTMX + Alpine.js + Chart.js
- OCR: Google Vision API

## 테스트 진행 순서 (TDD Red-Green-Refactor 사이클)

### Phase 1: Core Domain Models & Repository Layer

#### Test 1: User Model - Basic User Creation
- [x] should_create_user_with_name_and_initial_deposit
- [x] should_validate_user_name_is_required
- [x] should_initialize_deposit_to_zero_by_default

#### Test 2: User Repository - Firestore Integration
- [x] should_save_user_to_firestore
- [x] should_retrieve_user_by_id
- [x] should_list_all_users

#### Test 3: User Model - Deposit Management
- [x] should_add_deposit_amount
- [x] should_subtract_deposit_amount
- [x] should_not_allow_negative_deposit

#### Test 4: Store Model - Basic Store Management
- [x] should_create_store_with_name
- [x] should_enable_coupon_system_for_store
- [x] should_set_coupon_goal_for_store

#### Test 5: Store Repository - Firestore Integration
- [x] should_save_store_to_firestore
- [x] should_retrieve_store_by_id
- [x] should_find_store_by_name

### Phase 2: Receipt Processing & Transaction Management

#### Test 6: Receipt Model - Basic Receipt Structure
- [x] should_create_receipt_with_user_and_store
- [x] should_add_items_to_receipt
- [x] should_calculate_total_amount

#### Test 7: Receipt Item Model
- [x] should_create_receipt_item_with_name_and_price
- [x] should_set_default_quantity_to_one
- [x] should_calculate_item_total

#### Test 8: Transaction Service - Deposit Usage
- [x] should_process_transaction_with_deposit
- [x] should_process_transaction_without_deposit
- [x] should_reject_transaction_if_insufficient_deposit

#### Test 9: Receipt Repository
- [x] should_save_receipt_to_firestore
- [x] should_retrieve_receipts_by_user
- [x] should_retrieve_receipts_by_date_range

### Phase 3: Coupon System

#### Test 10: Coupon Model
- [x] should_create_coupon_for_user_and_store
- [x] should_increment_coupon_count
- [x] should_check_if_coupon_goal_reached

#### Test 11: Coupon Service
- [x] should_award_coupon_for_purchase
- [x] should_not_award_coupon_if_disabled
- [x] should_reset_coupon_when_goal_reached

#### Test 12: Coupon Repository
- [x] should_save_coupon_to_firestore
- [x] should_retrieve_coupons_by_user
- [x] should_update_coupon_count

### Phase 4: OCR Integration & Receipt Processing

#### Test 13: OCR Service
- [x] should_extract_text_from_receipt_image
- [x] should_parse_store_name_from_ocr_text
- [x] should_parse_items_and_prices_from_ocr_text
- [x] should_parse_date_from_ocr_text

#### Test 14: Receipt Parser
- [x] should_create_receipt_from_ocr_result
- [x] should_handle_missing_store_in_ocr
- [x] should_handle_invalid_price_format

### Phase 5: Web Interface - Basic Views

#### Test 15: User Selection View
- [x] should_display_user_selection_page
- [x] should_list_all_available_users
- [x] should_redirect_to_dashboard_when_user_selected

#### Test 16: User Dashboard View
- [x] should_display_user_deposit_balance
- [x] should_display_recent_transactions
- [x] should_display_coupon_progress

#### Test 17: Receipt Upload View
- [x] should_display_receipt_upload_form
- [x] should_handle_image_upload
- [x] should_display_ocr_results_for_confirmation

### Phase 6: Web Interface - Transaction Processing

#### Test 18: Receipt Confirmation Flow
- [x] should_display_parsed_receipt_for_confirmation
- [x] should_allow_user_to_select_target_user
- [x] should_allow_user_to_choose_deposit_usage
- [x] should_process_confirmed_receipt

#### Test 19: Transaction Success Flow
- [x] should_update_user_deposit_after_transaction
- [x] should_award_coupon_after_transaction
- [x] should_redirect_to_success_page

### Phase 7: Admin Interface

#### Test 20: Admin Authentication
- [x] should_require_admin_login
- [x] should_validate_admin_credentials
- [x] should_restrict_access_to_admin_pages

#### Test 21: Admin User Management
- [x] should_display_all_users_in_admin
- [x] should_allow_admin_to_create_user
- [x] should_allow_admin_to_add_deposit
- [x] should_allow_admin_to_delete_user

#### Test 22: Admin Store Management
- [x] should_display_all_stores_in_admin
- [x] should_allow_admin_to_create_store
- [x] should_allow_admin_to_toggle_coupon_system
- [x] should_allow_admin_to_set_coupon_goal

#### Test 23: Admin Transaction History
- [x] should_display_all_transactions
- [x] should_filter_transactions_by_user
- [x] should_filter_transactions_by_date
- [x] should_filter_transactions_by_store

### Phase 8: Charts & Visualization

#### Test 24: Chart Data Service
- [ ] should_generate_spending_trend_data
- [ ] should_generate_store_usage_distribution
- [ ] should_generate_coupon_progress_data

#### Test 25: Chart Integration
- [ ] should_render_spending_chart_on_dashboard
- [ ] should_render_store_distribution_chart
- [ ] should_render_coupon_progress_bars

### Phase 9: Error Handling & Edge Cases

#### Test 26: Error Handling
- [ ] should_handle_firestore_connection_errors
- [ ] should_handle_vision_api_errors
- [ ] should_handle_invalid_image_uploads
- [ ] should_handle_malformed_ocr_results

#### Test 27: Data Validation
- [ ] should_validate_receipt_amount_format
- [ ] should_validate_user_name_length
- [ ] should_validate_store_name_uniqueness

### Phase 10: Performance & Deployment

#### Test 28: Performance Optimization
- [ ] should_cache_user_data_efficiently
- [ ] should_optimize_firestore_queries
- [ ] should_compress_uploaded_images

#### Test 29: Cloud Functions Integration
- [ ] should_deploy_as_cloud_function
- [ ] should_handle_cold_starts
- [ ] should_configure_firestore_security_rules

## 개발 가이드라인

### TDD 사이클 준수
1. Red: 실패하는 테스트 작성
2. Green: 테스트를 통과시키는 최소한의 코드 작성
3. Refactor: 중복 제거 및 구조 개선 (테스트 통과 상태 유지)

### 커밋 규칙
- 구조적 변경과 동작적 변경을 별도 커밋
- 모든 테스트가 통과하는 상태에서만 커밋
- 한 번에 하나의 논리적 단위만 변경

### 코드 품질
- 중복 제거
- 명확한 의도 표현
- 단일 책임 원칙
- 가장 단순한 해결책 우선

### 라이브러리 관리 및 참조
- **uv 사용**: 의존성 설치 시 `uv add <package>`
- **Context7 MCP 활용**: 새로운 라이브러리 사용 전 반드시 최신 문서 확인
  - 예: `mcp__context7__resolve-library-id` → `mcp__context7__get-library-docs`
- **버전 관리**: pyproject.toml을 통한 의존성 관리

## 개발 환경 설정

### 1. 프로젝트 구조
```
deposit-tracker/
├── src/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── web/
├── tests/
├── pyproject.toml  # uv 기반 의존성 관리
├── main.py
└── config/
```

### 2. 패키지 관리 및 의존성 설치 (uv 사용)
```bash
# uv로 프로젝트 초기화
uv init

# 주요 의존성 설치
uv add flask
uv add functions-framework
uv add google-cloud-firestore
uv add google-cloud-vision
uv add pytest pytest-mock --dev
uv add black flake8 --dev
```

**⚠️ 중요**: 새로운 라이브러리 사용 전 Context7 MCP로 최신 문서 확인 필수!
- `mcp__context7__resolve-library-id <library-name>`
- `mcp__context7__get-library-docs <library-id>`

### 3. Firebase/Google Cloud 설정
- Firestore 데이터베이스 생성
- Vision API 활성화
- 서비스 계정 키 생성

### 4. 개발 도구 설정
**pyproject.toml 설정**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.flake8]
max-line-length = 88
extend-ignore = "E203,W503"
```

## 시작 방법

### 라이브러리 사용 워크플로우
```bash
# 1. 라이브러리 ID 확인
mcp__context7__resolve-library-id "flask"

# 2. 최신 문서 가져오기
mcp__context7__get-library-docs "/pallets/flask"

# 3. 의존성 추가
uv add flask

# 4. 구현 시작
```

### 개발 진행
1. **환경 설정**: `uv init` 및 기본 의존성 설치
2. **라이브러리 문서 확인**: Context7 MCP로 최신 문서 참조
3. **`go` 명령어**로 첫 번째 테스트 시작
4. **TDD 사이클**: Red-Green-Refactor 준수
5. **구조적 개선**과 기능 추가를 별도로 진행

## MVP 우선순위
1. Phase 1-3: 핵심 도메인 모델 및 저장소
2. Phase 4: OCR 통합
3. Phase 5-6: 기본 웹 인터페이스
4. Phase 7: 관리자 기능
5. Phase 8-10: 고급 기능 및 최적화

## 완료 기준
- [ ] 모든 테스트 통과
- [ ] 코드 품질 기준 충족 (no duplication, clear intent)
- [ ] MVP 기능 완전 구현
- [ ] Cloud Functions 배포 준비 완료

---

**시작하려면 "go" 명령어를 입력하세요!**