# 사내 컴퓨터 설정 가이드

사내 컴퓨터에서 이 프로젝트를 다운로드한 후 설정하는 방법입니다.

## 1. 저장소 클론

```bash
git clone https://github.com/williamtribe/TEXT_TO_SQL.git
cd TEXT_TO_SQL
```

## 2. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 3. 환경 변수 설정 (.env 파일 생성)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token

# MySQL (사내 데이터베이스)
MYSQL_HOST=mafiadb.crpu5sdj57pt.ap-northeast-2.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=secure-bonbon-478909-h1-ffa634ff64d6.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_WORKSHEET_NAME=TABLE_SUMMARY
GOOGLE_SHEETS_FEEDBACK_WORKSHEET_NAME=FEEDBACK
GOOGLE_SHEETS_LOG_WORKSHEET_NAME=LOG

# RAG Index (선택적, 자동 생성 가능)
RAG_INDEX_PATH=rag_index.json
```

## 4. Google Sheets 인증 파일 준비

`secure-bonbon-478909-h1-ffa634ff64d6.json` 파일을 프로젝트 루트 디렉토리에 배치하세요.
(이 파일은 보안상 GitHub에 올라가지 않습니다)

## 5. RAG Index 생성

Google Sheets에서 테이블 정보를 가져와 RAG index를 생성합니다:

```bash
source venv/bin/activate
python build_rag_index.py
```

이 명령어는:
- Google Sheets의 `TABLE_SUMMARY` 시트에서 테이블 정보를 읽어옵니다
- 각 테이블에 대한 임베딩을 생성합니다
- `rag_index.json` 파일을 생성합니다

## 6. 서버 실행

### 방법 1: FastAPI만 실행
```bash
source venv/bin/activate
uvicorn FASTAPI:app --reload --port 8000
```

### 방법 2: FastAPI + ngrok 함께 실행
```bash
source venv/bin/activate
./start_with_ngrok.sh
```

## 7. Slack App 설정

ngrok을 사용하는 경우, ngrok URL을 Slack App에 설정하세요:

- **Event Subscriptions URL**: `https://your-ngrok-url.ngrok-free.app/slack/events`
- **Slash Commands Request URL**: `https://your-ngrok-url.ngrok-free.app/slack/command`
- **Interactive Components Request URL**: `https://your-ngrok-url.ngrok-free.app/slack/interactivity`

## 주의사항

1. **`.env` 파일은 절대 GitHub에 올리지 마세요** (이미 .gitignore에 포함됨)
2. **Google Sheets 인증 파일(`*.json`)도 올라가지 않습니다** (이미 .gitignore에 포함됨)
3. **`rag_index.json`은 자동 생성되므로 올릴 필요 없습니다** (이미 .gitignore에 포함됨)
4. **사내 네트워크에서만 MySQL 데이터베이스에 접근 가능합니다**

## 문제 해결

### RAG Index 생성 실패
- Google Sheets 인증 파일 경로 확인
- Google Sheets 스프레드시트 ID 확인
- `TABLE_SUMMARY` 시트가 존재하는지 확인

### MySQL 연결 실패
- 사내 네트워크에 연결되어 있는지 확인
- VPN 연결 확인 (필요한 경우)
- MySQL 접속 정보 확인

### Slack 메시지 수신 안 됨
- ngrok이 실행 중인지 확인
- Slack App의 Event Subscriptions URL이 올바른지 확인
- Slack Bot Token이 유효한지 확인

