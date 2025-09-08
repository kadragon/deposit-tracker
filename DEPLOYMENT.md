# 🚀 배포 가이드 - 공동 영수증 분할 결제 시스템

## 📋 시스템 개요

4명의 사용자가 함께 카페/식당에서 생긴 영수증을 분할하여 각자의 예치금에서 차감하는 시스템입니다.

**핵심 기능**:
- 📷 영수증 OCR 자동 분석
- 🎯 물품별 사용자 배정
- 💰 다중 사용자 분할 결제
- 🎫 쿠폰 시스템 (실제 결제자 기준)
- 👨‍💼 관리자 예치금 관리

## 🛠️ 기술 스택

- **Backend**: Python 3.13 + Flask
- **Database**: Google Firestore
- **OCR**: Google Vision API + OpenAI GPT-4o-mini
- **Frontend**: Jinja2 + TailwindCSS/DaisyUI

## 📋 배포 체크리스트

### 1. 🛠️ 필수 의존성

```toml
# pyproject.toml에 정의된 의존성
[project]
requires-python = ">=3.13"
dependencies = [
    "flask>=3.1.2",
    "google-cloud-firestore>=2.21.0",
    "google-cloud-vision>=3.10.2",
    "openai>=1.37.0"
]
```

### 2. 🌍 환경 변수 설정

`.env` 파일 생성 (`.env.example` 참조):

```bash
# 🔑 Google Cloud 설정 (필수)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# 🤖 OpenAI API 설정 (OCR + LLM 파싱용)
LLM_PARSER_ENABLED=true
OPENAI_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini

# 🌐 Flask 설정
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
APP_SECRET_KEY=your-app-secret-key

# 👨‍💼 관리자 계정
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-admin-password

# 🛡️ 보안 옵션
ENABLE_CSRF=1
ENABLE_BULK_SAVE=1
```

### 3. ☁️ Google Cloud 설정

#### 3.1 Firestore Database 설정
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Firestore Database 생성 (Native Mode)
4. 보안 규칙 설정:

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 인증된 사용자만 접근 (개발용)
    match /{document=**} {
      allow read, write: if true;  // 프로덕션에서는 더 엄격하게 설정
    }
  }
}
```

#### 3.2 Google Vision API 활성화
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Vision API 활성화
3. 서비스 계정 생성 및 키 다운로드

#### 3.3 서비스 계정 권한 설정
필요한 역할:
- `Cloud Datastore User` (Firestore 접근)
- `Cloud Vision API Service Agent` (OCR 기능)

### 4. 🖥️ 배포 플랫폼별 가이드

#### A) 🐳 Docker 배포

**Dockerfile**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# uv 설치 (Python 패키지 매니저)
RUN pip install uv

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 소스 코드 복사
COPY . .

# 환경 변수 파일
COPY .env .env

EXPOSE 8080

# Flask 앱 실행
CMD ["uv", "run", "python", "-c", "from src.web.app import create_app; app = create_app(); app.run(host='0.0.0.0', port=8080)"]
```

**배포 명령어**:
```bash
# 이미지 빌드
docker build -t deposit-tracker .

# 컨테이너 실행
docker run -p 8080:8080 --env-file .env deposit-tracker
```

#### B) ☁️ Google Cloud Run 배포

**app.yaml** (선택사항):
```yaml
runtime: python313
service: deposit-tracker

env_variables:
  FLASK_ENV: production
  ENABLE_CSRF: "1"
  # 다른 환경 변수들...

automatic_scaling:
  min_instances: 0
  max_instances: 10
```

**배포 명령어**:
```bash
# gcloud CLI 설치 후
gcloud run deploy deposit-tracker \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars "FLASK_ENV=production,ENABLE_CSRF=1" \
  --memory 1Gi \
  --cpu 1
```

#### C) 🌊 Railway 배포

**railway.toml**:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uv run python -c 'from src.web.app import create_app; app = create_app(); app.run(host=\"0.0.0.0\", port=int(os.environ.get(\"PORT\", 8080)))'"
```

1. Railway 계정 생성
2. GitHub 레포지토리 연결
3. 환경 변수 설정 (Railway 대시보드에서)
4. 자동 배포 완료

#### D) 🟣 Render 배포

**render.yaml**:
```yaml
services:
  - type: web
    name: deposit-tracker
    env: python
    plan: free
    buildCommand: "pip install uv && uv sync"
    startCommand: "uv run python -c 'from src.web.app import create_app; app = create_app(); app.run(host=\"0.0.0.0\", port=int(os.environ.get(\"PORT\", 10000)))'"
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.0
      - key: FLASK_ENV
        value: production
```

### 5. 🗄️ 데이터베이스 초기 설정

#### Firestore Collections 구조:
```
📁 users/              # 사용자 정보
  📄 user1
    - name: "홍길동"
    - deposit: "50000"
    
📁 stores/             # 매장 정보
  📄 store1
    - name: "스타벅스"
    - coupon_enabled: true
    - coupon_goal: 5
    
📁 receipts/           # 영수증 데이터
  📄 receipt1
    - user_id: "user1"
    - store_id: "store1"
    - total: "25000"
    - items: [...]
    
📁 coupons/           # 쿠폰 데이터
  📄 coupon1
    - user_id: "user1"
    - store_id: "store1"
    - count: 3
    - goal: 5
```

#### 초기 데이터 생성 스크립트:
```python
# 관리자 계정으로 로그인 후 /admin/users에서 사용자 생성
# 또는 다음 스크립트 실행:

from src.repositories.user_repository import UserRepository
from src.models.user import User

# 4명의 기본 사용자 생성
users = [
    User(name="홍길동", deposit=50000),
    User(name="김철수", deposit=50000),
    User(name="박영희", deposit=50000),
    User(name="이영수", deposit=50000)
]

user_repo = UserRepository()
for user in users:
    user_repo.save(user)
```

### 6. 🔒 보안 설정

#### 프로덕션 권장 설정:
```bash
# 강력한 보안
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
APP_SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD=$(openssl rand -base64 20)

# CSRF 보호 활성화
ENABLE_CSRF=1

# HTTPS 강제 (리버스 프록시 설정)
# nginx.conf 또는 CDN에서 설정
```

#### Firestore 보안 규칙 (프로덕션용):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자는 자신의 데이터만 읽기 가능
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if false;  // 관리자만 수정 가능
    }
    
    // 영수증은 참여자만 읽기 가능
    match /receipts/{receiptId} {
      allow read: if request.auth != null && 
        request.auth.uid in resource.data.participants;
      allow write: if false;  // 앱에서만 생성
    }
  }
}
```

### 7. 📊 모니터링 & 로깅

#### Google Cloud Logging 설정:
```python
# src/web/app.py에 추가
import logging
from google.cloud import logging as cloud_logging

if os.environ.get('FLASK_ENV') == 'production':
    client = cloud_logging.Client()
    client.setup_logging()
```

#### 추천 모니터링 도구:
- **에러 추적**: [Sentry](https://sentry.io/)
- **성능 모니터링**: Google Cloud Operations
- **업타임 체크**: [UptimeRobot](https://uptimerobot.com/)

### 8. 🧪 배포 전 테스트

```bash
# 모든 테스트 실행
uv run pytest -q

# 보안 스캔
uv run bandit -r src/

# 환경 변수 확인
uv run python -c "
import os
checks = [
    ('GOOGLE_APPLICATION_CREDENTIALS', os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
    ('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY')),
    ('ADMIN_USERNAME', os.getenv('ADMIN_USERNAME')),
    ('SECRET_KEY', os.getenv('SECRET_KEY'))
]
for name, value in checks:
    status = '✅' if value else '❌'
    print(f'{status} {name}: {\"설정됨\" if value else \"설정 필요\"}')
"

# 로컬 서버 테스트
uv run python -c "
from src.web.app import create_app
app = create_app()
print('🚀 로컬 서버 시작: http://localhost:8080')
app.run(debug=False, port=8080)
"
```

## 🎯 배포 시나리오별 가이드

### 💰 비용 최적화 배포 (개인/소규모)

**플랫폼**: Railway, Render (Free Tier)
```yaml
# 무료 티어 설정
Memory: 512MB
CPU: 0.1 vCPU
Storage: 1GB
```

**서비스**:
- Firestore: 무료 할당량 (일 50,000 읽기/20,000 쓰기)
- Vision API: 월 1,000건 무료
- OpenAI API: GPT-4o-mini (~$0.001/1K tokens)

**예상 월 비용**: $0-15

### 🏢 프로덕션 배포 (팀/회사)

**플랫폼**: Google Cloud Run, AWS ECS
```yaml
# 프로덕션 설정  
Memory: 2GB
CPU: 1 vCPU
Min Instances: 1
Max Instances: 10
```

**서비스**:
- Firestore: Pay-as-you-go
- Vision API: $1.50/1,000 images
- Cloud Run: $0.24/1M requests
- Load Balancer + CDN

**예상 월 비용**: $50-200

## ⚡ 성능 최적화 팁

### 환경 변수 튜닝:
```bash
# 배치 저장 활성화 (대량 처리 시)
ENABLE_BULK_SAVE=1

# CSRF 비활성화 (API 전용 시)
ENABLE_CSRF=0

# 캐싱 설정
FLASK_CACHE_TYPE=simple
```

### Firestore 최적화:
```python
# 인덱스 설정 추천
# firestore.indexes.json
{
  "indexes": [
    {
      "collectionId": "receipts",
      "fields": [
        {"fieldPath": "user_id", "mode": "ASCENDING"},
        {"fieldPath": "created_at", "mode": "DESCENDING"}
      ]
    }
  ]
}
```

## 🆘 문제 해결

### 자주 발생하는 이슈:

#### 1. Firestore 권한 오류
```bash
❌ Error: Permission denied
✅ 해결: 서비스 계정 키 파일 경로 확인
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

#### 2. OCR 할당량 초과
```bash
❌ Error: Quota exceeded
✅ 해결: Vision API 할당량 확인 및 증량 요청
```

#### 3. CSRF 토큰 오류
```bash
❌ Error: CSRF token missing
✅ 해결: SECRET_KEY 설정 및 토큰 포함 확인
```

#### 4. OpenAI API 오류
```bash
❌ Error: Invalid API key
✅ 해결: OPENAI_API_KEY 확인 및 크레딧 잔액 점검
```

## 🎯 Go-Live 체크리스트

배포 전 최종 확인사항:

- [ ] 🔑 모든 API 키와 환경변수 설정 완료
- [ ] 🗄️ Firestore 데이터베이스 및 컬렉션 생성
- [ ] 👨‍💼 관리자 계정 생성 및 초기 사용자 등록
- [ ] 🧪 테스트 스위트 모두 통과 (161개 테스트)
- [ ] 🔒 보안 설정 (HTTPS, CSRF, 강력한 비밀번호)
- [ ] 📊 모니터링 및 로깅 설정
- [ ] 💰 비용 알림 설정 (예산 초과 방지)
- [ ] 📝 사용자 매뉴얼 및 관리자 가이드 준비

---

## 🎉 배포 완료!

이 가이드를 따르시면 **공동 영수증 분할 결제 시스템**을 성공적으로 배포할 수 있습니다.

### 📞 지원

- 📖 **문서**: README.md 참조
- 🐛 **버그 리포트**: GitHub Issues
- 💬 **질문**: 개발팀 연락처

**Happy Deploying! 🚀**