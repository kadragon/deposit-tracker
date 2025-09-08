# 공동 영수증 분할 결제 시스템 - TDD 개발 계획

## 📋 시스템 개요

**목적**: 4명의 사용자가 함께 카페/식당에 가서 생긴 영수증을 분할하여 각자의 예치금에서 차감하는 시스템

**핵심 프로세스**:
1. **관리자**가 각 사용자의 **예치금을 관리**
2. 누군가가 **공동 영수증을 업로드** (OCR로 물품 분석)
3. **물품별로 누가 먹었는지 선택** (분할 배정)
4. **각자의 예치금에서 해당 금액 차감**
5. **쿠폰은 실제 결제한 사람이 획득**

## 기술 스택
- Backend: Python (Flask + functions-framework)
- Database: Firestore
- Frontend: Jinja2 + TailwindCSS(DaisyUI) + HTMX + Alpine.js + Chart.js
- OCR: Google Vision API + OpenAI gpt-5-mini (LLM 파서)

## ✅ 완료된 작업 (Phase 1-7)

### 핵심 도메인 모델 & Repository Layer ✅
- User/Store 모델 및 Firestore 연동 완료
- Receipt/ReceiptItem 분할 기능 모델 완료
- Split Service (다중 사용자 분할 로직) 완료
- Transaction Service (다중 사용자 결제) 완료
- Coupon System (실제 결제자 기준) 완료

### OCR Integration & LLM Parser ✅
- Google Vision API 연동 완료
- LLM 기반 한국어 영수증 파서 완료 (정규식 폴백 포함)
- Receipt Parser 완료

### Web Interface ✅
- 기본 업로드 및 OCR 결과 확인 완료
- SSR 기반 Flask + Jinja2 + TailwindCSS/DaisyUI 구성 완료

### Admin Interface ✅
- 관리자 인증 및 사용자/예치금 관리 완료
- 매장 관리 및 쿠폰 설정 완료
- 트랜잭션 내역 조회 완료

### User Dashboard ✅
- 사용자별 대시보드 및 내역 조회 완료

---

## 🎯 다음 진행할 작업 (순서대로)

### Phase 5: 분할 UI 완성 (핵심 기능) ✅

#### Test 14: Receipt Upload & Analysis ✅
- [x] **should_display_items_for_user_assignment** - 물품별 사용자 배정 UI

#### Test 15: Item Assignment Interface ✅
- [x] **should_display_all_users_for_item_assignment** - 전체 사용자 목록 표시
- [x] **should_allow_assigning_items_to_users** - 물품을 사용자에게 배정
- [x] **should_support_item_sharing_selection** - 물품 공유 선택 기능
- [x] **should_show_real_time_amount_calculation** - 실시간 금액 계산
- [x] **should_validate_all_items_assigned_before_submit** - 모든 물품 배정 검증

#### Test 16: Split Payment Confirmation ✅
- [x] **should_display_per_user_payment_summary** - 사용자별 결제 요약
- [x] **should_show_insufficient_balance_warnings** - 잔액 부족 경고
- [x] **should_allow_payment_method_selection_per_user** - 사용자별 결제 방법 선택
- [x] **should_process_multi_user_payment** - 다중 사용자 결제 처리

### Phase 6: Admin Interface 보강

#### Test 18: Admin User & Deposit Management (보강)
- [ ] **should_show_detailed_deposit_history_per_user** - 사용자별 상세 예치금 내역
- [ ] **should_allow_bulk_deposit_addition** - 일괄 예치금 충전

#### Test 20: Admin Transaction History (보강)
- [ ] **should_display_split_payment_details** - 분할 결제 상세 내역
- [ ] **should_show_receipt_uploader_vs_payers** - 업로더 vs 결제자 구분
- [ ] **should_export_detailed_financial_report** - 상세 재무 리포트 내보내기

### Phase 7: User Dashboard 보강

#### Test 21: User Dashboard (보강)
- [ ] **should_show_split_payment_history** - 분할 결제 내역
- [ ] **should_display_receipts_uploaded_by_user** - 업로드한 영수증 목록
- [ ] **should_show_pending_split_requests** - 대기 중인 분할 요청

### Phase 8: Charts & Visualization

#### Test 22: Chart Data Service
- [ ] **should_generate_spending_breakdown_by_category** - 카테고리별 지출 분석
- [ ] **should_generate_group_spending_patterns** - 그룹 지출 패턴
- [ ] **should_generate_individual_vs_shared_expense_ratio** - 개인 vs 공유 지출 비율
- [ ] **should_generate_store_preference_by_group** - 그룹별 매장 선호도

#### Test 23: Chart Integration
- [ ] **should_render_group_expense_distribution** - 그룹 지출 분배 차트
- [ ] **should_render_individual_payment_trends** - 개인 결제 트렌드 차트
- [ ] **should_render_store_visit_frequency_chart** - 매장 방문 빈도 차트

### Phase 9: Error Handling & Edge Cases

#### Test 24: Split Payment Error Handling
- [ ] **should_handle_partial_insufficient_funds** - 부분 잔액 부족 처리
- [ ] **should_handle_unassigned_items** - 미배정 물품 처리
- [ ] **should_handle_duplicate_receipt_uploads** - 중복 영수증 업로드 방지
- [ ] should_handle_firestore_connection_errors
- [ ] should_handle_vision_api_errors
- [ ] should_handle_invalid_image_uploads
- [ ] should_handle_malformed_ocr_results

#### Test 25: Data Validation
- [ ] **should_validate_item_assignment_completeness** - 물품 배정 완성도 검증
- [ ] **should_validate_split_amounts_match_total** - 분할 금액 총합 검증
- [ ] should_validate_receipt_amount_format
- [ ] should_validate_user_name_length
- [ ] should_validate_store_name_uniqueness

### Phase 10: Performance & Deployment

#### Test 26: Performance Optimization
- [ ] **should_optimize_split_calculation_performance** - 분할 계산 성능 최적화
- [ ] should_cache_user_data_efficiently
- [ ] should_optimize_firestore_queries
- [ ] should_compress_uploaded_images

#### Test 27: Cloud Functions Integration
- [ ] should_deploy_as_cloud_function
- [ ] should_handle_cold_starts
- [ ] should_configure_firestore_security_rules

---

## 🎯 현재 우선순위

**1순위 (MVP 핵심)**: Phase 5 - 분할 UI 완성
- 물품별 사용자 배정 인터페이스
- 실시간 금액 계산 및 분할 확인
- 다중 사용자 결제 처리

**2순위**: Phase 6-7 - 관리자/사용자 대시보드 보강
- 상세 내역 조회 및 관리 기능

**3순위**: Phase 8-10 - 차트/에러처리/배포
- 분석 기능 및 안정성 확보

---

## 🚀 다음 작업 시작

**"go" 명령어를 입력하면 Test 14: should_display_items_for_user_assignment 부터 시작합니다.**

## 💡 핵심 변경사항 요약
- 개인별 영수증 → **공동 영수증 분할**
- 단일 결제 → **다중 사용자 분할 결제**
- 개인 쿠폰 → **실제 결제자 쿠폰**
- 사용자 관리 → **관리자 예치금 관리**