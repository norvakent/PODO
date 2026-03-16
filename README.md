# PODO

PODO는 실거래 안정성을 최우선으로 두고 시장 데이터, 전략 실행, AI 분석, 리스크 통제를 하나의 운영 체계로 통합하는 하이브리드 투자 운영 플랫폼이다.

## 프로젝트 개요

PODO는 다중 거래소 시세 수집, 전략 검증, 모의 실행, 통제된 실거래, AI 기반 분석, 포트폴리오 최적화를 하나의 운영 환경에서 수행할 수 있도록 설계된 하이브리드 투자 운영 플랫폼이다. 시스템은 장중 저지연 거래 서비스와 장후 분석·학습 작업을 분리해, 모델 실험이나 대규모 배치 연산이 실행 안정성을 훼손하지 않도록 설계된다.

### 핵심 가치

- `Safety First`: order execution, exposure control, and policy enforcement take precedence over model sophistication.
- `Standardization`: domestic securities and global crypto exchanges are abstracted behind a unified interface.
- `Isolation`: paper trading and model training run in isolated execution contexts to avoid contaminating production decisions.
- `Explainability`: every decision path should be auditable across strategy logic, AI outputs, and risk controls.

## 주요 기능

### 표준화된 거래소 인터페이스

PODO는 다음 API를 공통 계약으로 추상화하는 정규화 어댑터 계층을 제공한다.

- Korea Investment & Securities API
- Upbit API
- Binance API

각 커넥터는 거래소별 인증 방식, 시세 구조, 잔고 응답, 주문/체결 규격, 에러 코드를 공통 DTO와 서비스 인터페이스로 매핑한다. 이를 통해 Strategy Engine, Risk Manager, Portfolio Manager는 거래소별 분기 없이 동일한 도메인 모델 위에서 동작할 수 있다.

### React 차트 기반 빠른 주문

React 운영 콘솔은 차트 중심의 빠른 주문 플로우를 제공하며, 운영자는 다음 작업을 단일 화면에서 수행할 수 있다.

- inspect live market depth and recent fills,
- place limit or market orders directly from a chart context,
- preview policy checks before submission,
- confirm order routing and execution status in real time.

### 실전 데이터 기반 Paper Trading

Paper Trading은 실거래와 동일한 실시간 시세 피드를 사용하지만, 주문 체결과 자산 상태는 격리된 가상 계정 모델에서 처리된다. 주문, 체결, 포지션, 손익은 별도 실행 네임스페이스에서 추적되므로, 운영자는 실제 자본이나 실거래 정책을 건드리지 않고도 생산 환경과 유사한 조건에서 전략을 검증할 수 있다.

### Ollama 연동 및 학습 예약 시스템

PODO는 로컬 추론 및 모델 운영을 위해 Ollama와 연동하며, 다음과 같은 작업을 지원한다.

- market news summarization,
- event classification,
- sentiment and anomaly scoring,
- strategy support signal generation.

커스텀 모델 학습과 평가 작업은 장후 시간대로 예약되어, 장중 지연 예산을 보호하면서도 지속적인 모델 개선을 가능하게 한다.

### 포트폴리오 최적화

포트폴리오 계층은 기대수익률, 공분산, 변동성, 최대낙폭, 정책 제약조건을 입력으로 받아 목표 비중을 산출한다. 초기 설계 범위는 다음을 포함한다.

- mean-variance optimization,
- risk parity allocation,
- strategy-level capital budgeting,
- rebalance plans with exchange and market constraints.

## 시스템 아키텍처

PODO는 역할 분리를 명확히 한 폴리글랏 서비스 아키텍처를 사용한다.

- `NestJS`: operator APIs, exchange routing, order workflows, scheduling, policy enforcement, and operational management.
- `FastAPI`: AI inference, quant analytics, training orchestration, portfolio optimization, and anomaly detection.
- `React`: operator console, chart-based quick order UI, monitoring dashboards, and strategy management views.
- `PostgreSQL`: source of truth for orders, fills, positions, strategies, policies, schedules, experiments, and audit trails.
- `Redis`: queue, cache, distributed locks, and short-lived market/session state.
- `Ollama`: local model serving for LLM/NLP workloads.

### 서비스 간 통신

- `REST`는 운영자 요청, 전략 메타데이터 관리, 학습 작업 제출과 같은 제어 평면 요청에 사용된다.
- `gRPC`는 특징 점수 계산, 포트폴리오 최적화, 이상 행위 분류처럼 내부 서비스 간 고빈도·강타입 호출에 사용된다.
- `Event/Queue` 메시징은 예약 작업, 비동기 재학습, 알림 전파, 상태 동기화에 사용된다.

```mermaid
flowchart LR
    UI[React Operator Console] --> API[NestJS API Gateway]
    API --> CORE[Core Services]
    CORE --> GRPC[FastAPI Analytics gRPC]
    CORE --> REST[FastAPI Control REST]
    CORE --> DB[(PostgreSQL)]
    CORE --> REDIS[(Redis)]
    REST --> OLLAMA[Ollama API]
    GRPC --> OLLAMA
    CORE --> EX1[KIS Adapter]
    CORE --> EX2[Upbit Adapter]
    CORE --> EX3[Binance Adapter]
```

상세 설계는 [docs/architecture.md](/Users/norvakent/dev/PODO/docs/architecture.md)에서 다룬다.

## 제안 폴더 구조

```text
PODO/
├── README.md
├── docs/
│   └── architecture.md
├── apps/
│   ├── api-gateway/              # NestJS entrypoint
│   ├── ai-service/               # FastAPI entrypoint
│   └── web-console/              # React operator UI
├── packages/
│   ├── core/
│   │   ├── auth/
│   │   ├── exchange-router/
│   │   ├── scheduler/
│   │   ├── policy-engine/
│   │   └── observability/
│   ├── data/
│   │   ├── collectors/
│   │   ├── market-store/
│   │   ├── news-pipeline/
│   │   └── feature-store/
│   ├── engine/
│   │   ├── strategy-engine/
│   │   ├── backtester/
│   │   ├── paper-trader/
│   │   └── execution-engine/
│   └── management/
│       ├── portfolio-manager/
│       ├── risk-manager/
│       ├── anomaly-surveillance/
│       └── reporting/
├── infra/
│   ├── docker/
│   ├── compose/
│   └── migrations/
└── scripts/
```

## 차별화 기능

### AI 모델 생성

PODO의 AI 모델 생성 흐름은 단순 프롬프트 추론에 머무르지 않는다. 데이터셋 구성, 라벨링, 평가, 배포 패키징을 하나의 관리형 파이프라인으로 스케줄링한다.

1. market, news, and community data are normalized into training-ready datasets,
2. feature extraction and labeling jobs are executed in FastAPI workers,
3. Ollama-compatible models are benchmarked against validation scenarios,
4. approved models are versioned and promoted into inference endpoints,
5. deployment eligibility is gated by latency, drift, and quality thresholds.

### 비정상 매매 감시

비정상 매매 감시는 룰 기반 임계치와 ML 보조 점수를 결합해 다음 이상 징후를 탐지한다.

- excessive order frequency,
- unusual exposure concentration,
- price-impact anomalies,
- strategy behavior drift,
- exchange rejection bursts or throttling patterns.

탐지 결과는 감사 가능한 인시던트로 저장되며, 심각도에 따라 경고, 정책 강화, 강제 거래 중지까지 연결될 수 있다.

## 설치 및 설정

### 필수 환경 변수

```bash
# Core
NODE_ENV=development
TZ=Asia/Seoul
POSTGRES_URL=postgresql://podo:podo@postgres:5432/podo
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-me

# Exchange APIs
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_NO=your_kis_account

UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key

BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# AI / Analytics
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_DEFAULT_MODEL=llama3.1
MODEL_TRAINING_WINDOW=22:00-06:00
FASTAPI_GRPC_PORT=50051
FASTAPI_REST_PORT=8000
```

### Docker Compose 예시

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: podo
      POSTGRES_USER: podo
      POSTGRES_PASSWORD: podo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  api-gateway:
    build:
      context: .
      dockerfile: infra/docker/api-gateway.Dockerfile
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
      - ollama
    ports:
      - "3000:3000"

  ai-service:
    build:
      context: .
      dockerfile: infra/docker/ai-service.Dockerfile
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
      - ollama
    ports:
      - "8000:8000"
      - "50051:50051"

  web-console:
    build:
      context: .
      dockerfile: infra/docker/web-console.Dockerfile
    env_file:
      - .env
    depends_on:
      - api-gateway
    ports:
      - "5173:5173"

volumes:
  postgres_data:
  ollama_data:
```

### 실행 절차

```bash
cp .env.example .env
docker compose up -d --build
```

권장 기동 순서:

1. infrastructure services (`postgres`, `redis`, `ollama`)
2. backend services (`api-gateway`, `ai-service`)
3. frontend console (`web-console`)

## 초기 구현 범위

- unified exchange adapter contracts for KIS, Upbit, and Binance,
- live market ingestion and paper trading baseline,
- React dashboard with quick-order chart interaction,
- Ollama-backed inference endpoints and scheduled training jobs,
- portfolio optimization and abnormal trading surveillance foundations.

## 문서

- Roadmap: [PROJECT_ROADMAP.md](/Users/norvakent/dev/PODO/PROJECT_ROADMAP.md)
- Architecture Specification: [docs/architecture.md](/Users/norvakent/dev/PODO/docs/architecture.md)
