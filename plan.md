# 공동 영수증 분할 결제 시스템 - TDD 개발 계획

## 📋 시스템 개요

**목적**: 4명의 사용자가 함께 카페/식당에 가서 생긴 영수증을 분할하여 각자의 예치금에서 차감하는 시스템

**핵심 프로세스**:

1. **관리자**가 각 사용자의 **예치금을 관리**
2. 누군가가 **공동 영수증을 업로드** (OCR로 물품 분석)
3. **물품별로 누가 먹었는지 선택** (분할 배정)
4. **각자의 예치금에서 해당 금액 차감**
5. **쿠폰은 실제 결제한 사람이 획득**

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

## 🎯 새로운 시나리오 기반 테스트 진행 순서

### Phase 1: Core Domain Models & Repository Layer

#### Test 1: User Model - 예치금 관리

- [x] should_create_user_with_name_and_initial_deposit
- [x] should_validate_user_name_is_required
- [x] should_initialize_deposit_to_zero_by_default
- [x] should_add_deposit_amount
- [x] should_subtract_deposit_amount
- [x] should_not_allow_negative_deposit

#### Test 2: User Repository - Firestore Integration

- [x] should_save_user_to_firestore
- [x] should_retrieve_user_by_id
- [x] should_list_all_users

#### Test 3: Store Model - 매장 및 쿠폰 관리

- [x] should_create_store_with_name
- [x] should_enable_coupon_system_for_store
- [x] should_set_coupon_goal_for_store

#### Test 4: Store Repository - Firestore Integration

- [x] should_save_store_to_firestore
- [x] should_retrieve_store_by_id
- [x] should_find_store_by_name

### Phase 2: 공동 영수증 및 분할 시스템

#### Test 5: Receipt Model - 공동 영수증 구조

- [x] should_create_receipt_with_store_and_total_amount
- [x] should_add_items_to_receipt
- [x] should_calculate_total_amount
- [x] **should_support_multiple_users_per_receipt** (새로운 요구사항)
- [x] **should_track_who_uploaded_receipt** (새로운 요구사항)

#### Test 6: Receipt Item Model - 물품별 분할

- [x] should_create_receipt_item_with_name_and_price
- [x] should_set_default_quantity_to_one
- [x] should_calculate_item_total
- [x] **should_assign_item_to_specific_user** (새로운 핵심 기능)
- [x] **should_support_item_sharing_between_users** (새로운 기능)
- [x] **should_calculate_per_user_amount_for_shared_items** (새로운 기능)

#### Test 7: Split Service - 분할 결제 로직

- [x] **should_split_receipt_items_by_user_assignment** (새로운 핵심 서비스)
- [x] **should_calculate_individual_amounts** (새로운 기능)
- [x] **should_validate_all_items_are_assigned** (새로운 검증)
- [x] **should_handle_shared_items_proportionally** (새로운 기능)

#### Test 8: Transaction Service - 다중 사용자 결제

- [x] should_process_transaction_with_deposit
- [x] should_process_transaction_without_deposit
- [x] should_reject_transaction_if_insufficient_deposit
- [x] **should_process_split_payment_for_multiple_users** (새로운 핵심 기능)
- [x] **should_handle_partial_payment_failures** (새로운 기능)
- [x] **should_rollback_on_insufficient_funds** (새로운 기능)

### Phase 3: Repository Layer 확장

#### Test 9: Receipt Repository - 분할 영수증 저장

- [x] should_save_receipt_to_firestore
- [x] should_retrieve_receipts_by_user
- [x] should_retrieve_receipts_by_date_range
- [x] **should_save_receipt_with_user_assignments** (새로운 기능)
- [x] **should_retrieve_receipts_by_uploader** (새로운 기능)
- [x] **should_retrieve_split_transactions_by_user** (새로운 기능)

#### Test 10: Coupon System - 실제 결제자 기준

- [x] should_create_coupon_for_user_and_store
- [x] should_increment_coupon_count
- [x] should_check_if_coupon_goal_reached
- [x] **should_award_coupon_only_to_actual_payers** (수정된 로직)
- [x] **should_not_award_coupon_for_zero_amount_users** (새로운 검증)

#### Test 11: Coupon Service & Repository

- [x] should_award_coupon_for_purchase
- [x] should_not_award_coupon_if_disabled
- [x] should_reset_coupon_when_goal_reached
- [x] should_save_coupon_to_firestore
- [x] should_retrieve_coupons_by_user
- [x] should_update_coupon_count

### Phase 4: OCR Integration & Receipt Processing

#### Test 12: OCR Service - 물품 분석

- [x] should_extract_text_from_receipt_image
- [x] should_parse_store_name_from_ocr_text
- [x] should_parse_items_and_prices_from_ocr_text
- [x] should_parse_date_from_ocr_text

#### Test 13: Receipt Parser - 분할용 데이터 구조

- [x] should_create_receipt_from_ocr_result
- [x] should_handle_missing_store_in_ocr
- [x] should_handle_invalid_price_format
- [x] **should_create_receipt_items_ready_for_assignment** (새로운 기능)

#### LLM 기반 파서 도입 계획 (OpenAI gpt-5-mini)

목표: Google Vision OCR 결과 텍스트에서 정규식 대신 LLM을 사용해 물품/가격/날짜/매장명을 구조화해 추출. 한국어 영수증 포맷 변동에도 강인한 파싱 품질 확보.

접근 방식:

- 프롬프트 설계: 시스템 프롬프트에 역할/출력형식을 고정하고, 사용자 메시지에 OCR 원문 텍스트를 그대로 제공. 지시사항은 “한국 영수증에서 항목명과 금액(원 단위)을 추출, 숫자는 쉼표 제거, 할인/총계/전화 등 메타라인은 제외”로 명시.
- 구조화 출력: JSON 스키마 강제. 필드: `store: string|null`, `date: string|null (YYYY-MM-DD HH:MM:SS)`, `items: [{name: string, price: number, quantity: number}]`.
- 모델/파라미터: `model=gpt-5-mini`, `temperature=0`, `max_output_tokens`는 500±. 토큰 절약 위해 OCR 원문이 6–8KB 초과 시 헤더/푸터 우선 선택 요약 후 2단계 호출 고려.
- 호출 방식: OpenAI Python SDK Responses API 사용. 실패 시 1회 재시도(지수 백오프). JSON 파싱 실패 시 JSON 검사 후 수정 프롬프트로 1회 복구.
- 폴백 전략: 기본은 LLM-우선. LLM이 빈 결과를 반환하거나 스키마 검증 실패 시 현재 정규식 파서로 폴백(점진적 도입 안정성).
- 성능/비용: gpt-5-mini 1건당 수백원 미만 예상(텍스트 길이에 비례). 장바구니 라인 10~30개 기준 평균 300–800ms. 비동기/배치 호출로 UI 체감 시간 감소.
- 보안/프라이버시: 결제정보/전화번호 등 PII 마스킹 후 전송. `.env`의 `OPENAI_API_KEY` 사용, 서버사이드에서만 호출.

테스트 추가(Phase 4 연계):

- [x] **should_parse_items_with_llm_for_korean_receipt**
- [x] **should_ignore_meta_lines_with_llm** (TEL/총계/할인 제외)
- [x] **should_return_valid_json_schema_from_llm**
- [x] **should_fallback_to_regex_when_llm_empty**
- [x] **should_extract_store_and_date_with_llm**

단계별 작업:

1. LLM 파서 서비스 추가: `LLMReceiptParser` (OpenAI SDK 의존)
2. 공통 인터페이스: `parse(ocr_text) -> ParsedReceiptDTO`로 정규식/LLM 교체 가능 구조
3. 환경변수/플래그: `OPENAI_API_KEY`, `LLM_PARSER_ENABLED=true`, `LLM_MODEL=gpt-5-mini`
4. 프롬프트/스키마 정의 및 단위테스트 작성
5. 웹 경로 통합: 업로드 후 파서 선택(플래그 기반) 및 결과 확인 화면 동일 유지
6. 관측성: LLM 응답/토큰/지연 로깅(민감정보 마스킹), 실패율 모니터링
7. A/B 샘플 평가: 30개 영수증 정답셋으로 정규식 대비 정밀도/재현율 측정

예시 스키마(요약):

```
{
  "store": "스타벅스 강남점",
  "date": "2024-09-01 12:34:56",
  "items": [
    {"name": "아메리카노", "price": 4500, "quantity": 1},
    {"name": "치즈케이크", "price": 6200, "quantity": 1}
  ]
}
```

### Phase 5: Web Interface - 분할 UI

#### SSR UI 구성 계획 (Flask + Jinja2 + TailwindCSS/DaisyUI)

목표: 서버사이드 렌더링(SSR)로 빠르게 기본 UI를 구축하고, DaisyUI 기반 디자인 시스템으로 컴포넌트 일관성을 확보. 초기에는 CDN 방식으로 속도/단순성을 우선하고, 추후 Tailwind 로컬 빌드로 최적화 전환.

정보 구조 및 라우트

- 사용자: `/`(사용자 선택) → `/dashboard/<user_id>`(대시보드)
- 영수증: `/upload`(업로드/POST) → OCR 결과 확인(`/receipts/<id>/review`) → 물품 배정(`/receipts/<id>/assign`) → 분할 확인(`/receipts/<id>/confirm`)
- 관리자: `/admin/login`, `/admin/users`, `/admin/stores`, `/admin/transactions`

템플릿 구조(Jinja2)

- `templates/base.html`: 공통 레이아웃, 네비게이션, 컨테이너, 플래시/에러 영역
- `templates/components/macros.html`: 버튼/인풋/셀렉트/모달/토스트/배지 매크로로 컴포넌트 표준화
- `templates/partials/*.html`: 테이블 행, 아이템 배정 카드, 합계 요약 등 부분 템플릿
- 페이지 템플릿: `index.html`, `dashboard.html`, `upload.html`, `receipt_review.html`, `assign.html`, `split_confirm.html`, `admin/*.html`

스타일 가이드(Tailwind + DaisyUI)

- MVP: CDN 우선
  - `<link>`: DaisyUI CDN, TailwindCDN 사용 → 즉시 적용, 빌드 과정 없음
  - DaisyUI 테마: `light`(기본) + 다크토글 옵션 준비
- 최적화 단계: 로컬 빌드
  - `tailwind.config.js` + `postcss.config.js` 구성, purge 경로: `templates/**/*.html`, `src/web/**/*.py`
  - DaisyUI 플러그인 추가, 커스텀 테마 토큰 정의(brand 색상/간격/라운딩)

상호작용 패턴

- HTMX: 아이템 배정, 수량/공유 토글 시 부분 갱신(행 단위 partial 반환)으로 서버 일관성 유지
- Alpine.js(선택): 모달/토스트 등 경량 상태 관리
- 폼 검증: 서버 검증 우선, 필수 필드/형식 오류는 DaisyUI `alert`로 표시

디자인 일관성 확보 방안

- 컴포넌트 매크로 강제 사용: 버튼/인풋/테이블 헤더/배지 색상/크기 통일
- 레이아웃 단위 스케일: 컨테이너 폭, 카드 패딩, 섀도우 단계 표준 정의
- 아이콘/상태 컬러 토큰 통일: success/info/warn/danger 스케일 지정

구현 체크리스트(단계)

1) 템플릿 디렉토리/베이스 레이아웃 생성(`base.html` + 네비/플래시)
2) 사용자 선택/대시보드 뷰를 SSR로 전환(`render_template`)
3) 업로드 → OCR 결과 확인 화면(항목 목록/합계/수정) 구성
4) 배정 화면: 사용자 선택/공유 비율 UI + 실시간 합계(HTMX)
5) 분할 확인 화면: 사용자별 금액 요약/경고/확정 버튼
6) 관리자 화면: 사용자/매장/트랜잭션 리스트 표준 테이블로 정렬/필터 UI
7) 스타일 토큰/컴포넌트 매크로 확정 및 적용 린팅(리뷰 체크리스트)

UI 관련 테스트(보강)

- [ ] **should_render_index_with_user_list_template**
- [ ] **should_render_dashboard_with_receipts_and_coupons**
- [ ] **should_render_upload_and_review_pages**
- [ ] **should_render_assignment_ui_with_users_and_items**
- [ ] **should_render_split_confirmation_summary**

#### Test 14: Receipt Upload & Analysis

- [x] should_display_receipt_upload_form
- [x] should_handle_image_upload
- [x] should_display_ocr_results_for_confirmation
- [ ] **should_display_items_for_user_assignment** (새로운 핵심 UI)

#### Test 15: Item Assignment Interface

- [ ] **should_display_all_users_for_item_assignment** (새로운 UI)
- [ ] **should_allow_assigning_items_to_users** (새로운 UI)
- [ ] **should_support_item_sharing_selection** (새로운 UI)
- [ ] **should_show_real_time_amount_calculation** (새로운 UI)
- [ ] **should_validate_all_items_assigned_before_submit** (새로운 검증)

#### Test 16: Split Payment Confirmation

- [ ] **should_display_per_user_payment_summary** (새로운 UI)
- [ ] **should_show_insufficient_balance_warnings** (새로운 UI)
- [ ] **should_allow_payment_method_selection_per_user** (새로운 UI)
- [ ] **should_process_multi_user_payment** (새로운 기능)

### Phase 6: Admin Interface - 예치금 관리 중심

#### Test 17: Admin Authentication

- [x] should_require_admin_login
- [x] should_validate_admin_credentials
- [x] should_restrict_access_to_admin_pages

#### Test 18: Admin User & Deposit Management

- [x] should_display_all_users_in_admin
- [x] should_allow_admin_to_create_user
- [x] should_allow_admin_to_add_deposit
- [x] should_allow_admin_to_delete_user
- [ ] **should_show_detailed_deposit_history_per_user** (새로운 기능)
- [ ] **should_allow_bulk_deposit_addition** (새로운 편의 기능)

#### Test 19: Admin Store Management

- [x] should_display_all_stores_in_admin
- [x] should_allow_admin_to_create_store
- [x] should_allow_admin_to_toggle_coupon_system
- [x] should_allow_admin_to_set_coupon_goal

#### Test 20: Admin Transaction History - 분할 결제 내역

- [x] should_display_all_transactions
- [x] should_filter_transactions_by_user
- [x] should_filter_transactions_by_date
- [x] should_filter_transactions_by_store
- [ ] **should_display_split_payment_details** (새로운 기능)
- [ ] **should_show_receipt_uploader_vs_payers** (새로운 기능)
- [ ] **should_export_detailed_financial_report** (새로운 기능)

### Phase 7: 사용자 대시보드

#### Test 21: User Dashboard - 분할 결제 내역

- [x] should_display_user_deposit_balance
- [x] should_display_recent_transactions
- [x] should_display_coupon_progress
- [ ] **should_show_split_payment_history** (새로운 기능)
- [ ] **should_display_receipts_uploaded_by_user** (새로운 기능)
- [ ] **should_show_pending_split_requests** (새로운 기능)

### Phase 8: Charts & Visualization - 분할 결제 분석

#### Test 22: Chart Data Service

- [ ] **should_generate_spending_breakdown_by_category** (수정된 기능)
- [ ] **should_generate_group_spending_patterns** (새로운 기능)
- [ ] **should_generate_individual_vs_shared_expense_ratio** (새로운 기능)
- [ ] **should_generate_store_preference_by_group** (새로운 기능)

#### Test 23: Chart Integration

- [ ] **should_render_group_expense_distribution** (새로운 차트)
- [ ] **should_render_individual_payment_trends** (새로운 차트)
- [ ] **should_render_store_visit_frequency_chart** (새로운 차트)

### Phase 9: Error Handling & Edge Cases

#### Test 24: Split Payment Error Handling

- [ ] should_handle_firestore_connection_errors
- [ ] should_handle_vision_api_errors
- [ ] should_handle_invalid_image_uploads
- [ ] should_handle_malformed_ocr_results
- [ ] **should_handle_partial_insufficient_funds** (새로운 에러 케이스)
- [ ] **should_handle_unassigned_items** (새로운 검증)
- [ ] **should_handle_duplicate_receipt_uploads** (새로운 검증)

#### Test 25: Data Validation

- [ ] should_validate_receipt_amount_format
- [ ] should_validate_user_name_length
- [ ] should_validate_store_name_uniqueness
- [ ] **should_validate_item_assignment_completeness** (새로운 검증)
- [ ] **should_validate_split_amounts_match_total** (새로운 검증)

### Phase 10: Performance & Deployment

#### Test 26: Performance Optimization

- [ ] should_cache_user_data_efficiently
- [ ] should_optimize_firestore_queries
- [ ] should_compress_uploaded_images
- [ ] **should_optimize_split_calculation_performance** (새로운 최적화)

#### Test 27: Cloud Functions Integration

- [ ] should_deploy_as_cloud_function
- [ ] should_handle_cold_starts
- [ ] should_configure_firestore_security_rules

## 🔄 새로운 핵심 워크플로우

### 1. 영수증 업로드 & 분석

```
업로더(사용자 A) → 영수증 이미지 업로드 → OCR 분석 → 물품 목록 생성
```

### 2. 물품 분할 배정

```
물품 목록 → 각 물품별 사용자 선택 → 공유 물품 비율 설정 → 개인별 금액 계산
```

### 3. 분할 결제 처리

```
개인별 금액 확인 → 예치금 잔액 검증 → 다중 사용자 동시 결제 → 쿠폰 지급 (실제 결제자만)
```

### 4. 관리자 예치금 관리

```
사용자별 잔액 모니터링 → 예치금 충전 → 사용 내역 추적 → 정산 리포트 생성
```

## 📊 데이터 모델 변경사항

### Receipt Model 확장

```python
class Receipt:
    uploader_id: str          # 영수증 업로드한 사용자
    participants: List[str]   # 참여 사용자 목록
    split_amounts: Dict[str, Decimal]  # 사용자별 결제 금액
    is_split_complete: bool   # 분할 배정 완료 여부
```

### ReceiptItem Model 확장

```python
class ReceiptItem:
    assigned_users: List[str]        # 배정된 사용자 목록
    sharing_type: str               # 'individual' | 'shared'
    user_amounts: Dict[str, Decimal] # 사용자별 분담 금액
```

### SplitTransaction Model 추가

```python
class SplitTransaction:
    receipt_id: str
    user_transactions: List[UserTransaction]
    total_amount: Decimal
    created_at: datetime
```

## 🎯 MVP 우선순위 (수정됨)

1. **Phase 1-2**: 핵심 도메인 모델 + 분할 로직
2. **Phase 3-4**: 저장소 확장 + OCR 통합
3. **Phase 5**: 분할 UI (핵심 기능)
4. **Phase 6**: 관리자 예치금 관리
5. **Phase 7-10**: 대시보드, 분석, 최적화

## 완료 기준

- [ ] 4명 사용자 공동 영수증 분할 기능 완성
- [ ] 물품별 사용자 배정 UI 완성
- [ ] 다중 사용자 동시 결제 처리
- [ ] 관리자 예치금 관리 시스템
- [ ] 모든 테스트 통과
- [ ] MVP 기능 완전 구현

---

**🚀 새로운 시나리오로 개발 시작하려면 "go" 명령어를 입력하세요!**

**💡 핵심 변경사항**:

- 개인별 영수증 → **공동 영수증 분할**
- 단일 결제 → **다중 사용자 분할 결제**
- 개인 쿠폰 → **실제 결제자 쿠폰**
- 사용자 관리 → **관리자 예치금 관리**
