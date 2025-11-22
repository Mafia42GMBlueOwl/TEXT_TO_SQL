#!/bin/bash

# FastAPI 서버와 ngrok을 함께 실행하는 스크립트
# 사용법: ./start_with_ngrok.sh [포트번호]

echo "🚀 FastAPI + ngrok 서버 실행"
echo "============================"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 가상환경을 생성하세요."
    exit 1
fi

# ngrok 확인
if ! command -v ngrok &> /dev/null; then
    echo ""
    echo "❌ ngrok이 설치되어 있지 않습니다."
    echo "   설치: brew install ngrok/ngrok/ngrok"
    exit 1
fi

# 기존 ngrok 프로세스 종료
pkill -f ngrok 2>/dev/null
sleep 1

# 가상환경 활성화
source venv/bin/activate

# 포트 설정 (기본값: 8000)
PORT=${1:-8000}

# FastAPI 서버가 이미 실행 중인지 확인
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  포트 $PORT가 이미 사용 중입니다."
    echo "   기존 서버를 사용하거나 다른 포트를 선택하세요."
    echo ""
    read -p "기존 서버를 종료하고 새로 시작하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 기존 서버 종료 중..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null
        sleep 2
    else
        echo "기존 서버를 사용합니다."
        EXISTING_SERVER=true
    fi
fi

if [ "$EXISTING_SERVER" != "true" ]; then
    echo ""
    echo "📡 FastAPI 서버 시작 (포트: $PORT)..."
    echo ""
    
    # 백그라운드에서 FastAPI 서버 실행
    uvicorn FASTAPI:app --reload --host 0.0.0.0 --port $PORT &
    FASTAPI_PID=$!
    
    # 서버가 시작될 때까지 잠시 대기
    sleep 3
    
    echo "✅ FastAPI 서버 시작 완료 (PID: $FASTAPI_PID)"
else
    FASTAPI_PID=""
fi

echo ""
echo "🌐 ngrok 터널 시작..."
echo "   ngrok URL을 Slack App의 Event Subscriptions URL에 설정하세요!"
echo ""

# ngrok 실행 (포트 $PORT로 터널링)
# --pooling-enabled 옵션으로 기존 엔드포인트 재사용 가능
ngrok http $PORT --log=stdout

# 종료 시 FastAPI 프로세스도 함께 종료
if [ ! -z "$FASTAPI_PID" ]; then
    trap "kill $FASTAPI_PID 2>/dev/null" EXIT
fi
