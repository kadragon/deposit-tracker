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

## 🎯 **우선 진행할 작업 - UI 구현 (Phase 1)**

### **🚨 현재 상황**: 백엔드 완료, 템플릿 없음
- **백엔드 기능**: 100% 완료 (161개 테스트 통과)
- **프론트엔드**: 0% (템플릿 파일 전혀 없음)
- **현재 웹**: 텍스트만 출력 ("user-selection밥앨리스카드래곤")

---

### **Phase UI-1: 기본 템플릿 구조 생성**

#### Test UI-1: Base Template & User Selection ✅
- [x] **should_render_base_template_with_tailwind** - 기본 Tailwind CSS 템플릿
- [x] **should_display_user_selection_form** - 사용자 선택 폼 UI
- [x] **should_render_user_cards_with_deposit_info** - 사용자 카드 + 예치금 표시

#### Test UI-2: User Dashboard Template ✅ 
- [x] **should_render_user_dashboard_layout** - 사용자 대시보드 레이아웃
- [x] **should_display_current_balance_prominently** - 현재 잔액 강조 표시
- [x] **should_show_recent_transactions_list** - 최근 거래 내역 리스트
- [x] **should_render_upload_receipt_button** - 영수증 업로드 버튼

#### Test UI-3: Receipt Upload Interface ✅
- [x] **should_render_file_upload_dropzone** - 파일 업로드 드래그앤드롭
- [x] **should_show_upload_progress_indicator** - 업로드 진행률 표시
- [x] **should_display_ocr_processing_spinner** - OCR 처리 스피너
- [x] **should_render_ocr_results_preview** - OCR 결과 미리보기

### **Phase UI-2: 분할 결제 인터페이스** (백엔드 완료, UI 미구현)

#### Test UI-4: Item Assignment Interface ✅
- [x] **should_render_items_list_with_checkboxes** - 물품 목록 + 체크박스
- [x] **should_display_user_avatars_for_assignment** - 사용자별 아바타 배정
- [x] **should_show_real_time_calculation_sidebar** - 실시간 계산 사이드바
- [x] **should_render_split_summary_modal** - 분할 요약 모달

#### Test UI-5: Payment Confirmation ✅
- [x] **should_render_payment_summary_cards** - 결제 요약 카드들
- [x] **should_show_insufficient_balance_alerts** - 잔액 부족 경고
- [x] **should_render_payment_confirmation_flow** - 결제 확인 플로우

### **Phase UI-3: 관리자 인터페이스** ✅

#### Test UI-6: Admin Dashboard ✅
- [x] **should_render_admin_navigation_menu** - 관리자 네비게이션
- [x] **should_display_users_management_grid** - 사용자 관리 그리드
- [x] **should_render_deposit_management_forms** - 예치금 관리 폼
- [x] **should_show_transaction_history_table** - 거래 내역 테이블

#### Test UI-7: Store Management ✅ 
- [x] **should_render_stores_list_with_actions** - 매장 목록 + 액션들
- [x] **should_display_coupon_settings_toggles** - 쿠폰 설정 토글
- [x] **should_render_store_analytics_charts** - 매장 분석 차트

---

## ✅ **완료된 백엔드 기능 (Phase 1-7)**

### 핵심 도메인 & 서비스 Layer ✅
- User/Store/Receipt/Coupon 모델 완료
- 분할 결제 로직 완료 
- OCR + LLM 파서 완료
- Admin/User API 완료

### Phase 5-7: UI 로직 (백엔드) ✅
#### Test 14-16: 분할 UI 백엔드 ✅
- [x] 물품별 사용자 배정 로직
- [x] 실시간 금액 계산 
- [x] 다중 사용자 결제 처리

#### Test 18, 20-21: 대시보드 백엔드 ✅
- [x] 관리자 사용자/예치금 관리
- [x] 거래 내역 및 리포트 
- [x] 사용자 대시보드 데이터

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

---

## 🎯 **현재 우선순위 - UI 구현**

**🚨 1순위 (긴급)**: Phase UI-1 - 기본 템플릿 구조
- 사용자 선택 폼 (현재 텍스트만 출력됨)
- 기본 대시보드 레이아웃
- 영수증 업로드 UI

**2순위**: Phase UI-2 - 분할 결제 인터페이스  
- 물품 배정 UI (백엔드 완료)
- 실시간 계산 UI

**3순위**: Phase UI-3 - 관리자 인터페이스
- 사용자 관리 UI (백엔드 완료)

---

## 🚀 **다음 작업 시작**

**"go" 명령어를 입력하면 Test UI-1: should_render_base_template_with_tailwind 부터 시작합니다.**

### 📋 **UI 개발 접근법**
1. **TDD 방식 유지**: 각 템플릿 기능별로 테스트 먼저 작성
2. **Jinja2 + TailwindCSS**: 기존 기술 스택 활용
3. **Progressive Enhancement**: 기본 HTML부터 시작하여 점진적 개선

## 💡 핵심 변경사항 요약
- 개인별 영수증 → **공동 영수증 분할**
- 단일 결제 → **다중 사용자 분할 결제**
- 개인 쿠폰 → **실제 결제자 쿠폰**
- 사용자 관리 → **관리자 예치금 관리**