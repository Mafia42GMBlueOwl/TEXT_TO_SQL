# build_rag_index.py

import pandas as pd
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()  # .env 불러오기

# 환경 변수에서 경로 가져오기 (없으면 기본값)
EXCEL_PATH = os.getenv("EXCEL_PATH", "")  # 선택적: Excel 파일 경로
OUTPUT_JSON = os.getenv("RAG_INDEX_PATH", "rag_index.json")  # 기본값: 현재 디렉토리

# Google Sheets 설정
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
# RAG index 생성을 위해서는 항상 TABLE_SUMMARY 시트 사용
GOOGLE_SHEETS_WORKSHEET_NAME = "TABLE_SUMMARY"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_data_from_google_sheets():
    """Google Sheets에서 데이터 가져오기"""
    if not GOOGLE_SHEETS_CREDENTIALS_PATH or not GOOGLE_SHEETS_SPREADSHEET_ID:
        return None
    
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_PATH, scopes=scopes)
        gc = gspread.authorize(creds)
        
        spreadsheet = gc.open_by_key(GOOGLE_SHEETS_SPREADSHEET_ID)
        
        # 시트 목록 확인
        print(f"📋 사용 가능한 시트 목록:")
        for sheet in spreadsheet.worksheets():
            print(f"   - {sheet.title}")
        
        worksheet = spreadsheet.worksheet(GOOGLE_SHEETS_WORKSHEET_NAME)
        print(f"✅ 시트 '{GOOGLE_SHEETS_WORKSHEET_NAME}' 열기 완료")
        
        # 먼저 헤더 행 확인
        header_row = worksheet.row_values(1)
        print(f"📋 시트 헤더: {header_row}")
        
        # 모든 값 가져오기
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            print("⚠️ 데이터가 없습니다.")
            return None
        
        # 헤더 매핑 (다양한 헤더 이름 지원)
        header_map = {}
        for idx, header in enumerate(header_row):
            header_lower = header.lower().strip()
            if 'table' in header_lower or '테이블' in header_lower:
                header_map['table_name'] = idx
            elif 'column' in header_lower or '컬럼' in header_lower or '열' in header_lower:
                header_map['columns'] = idx
            elif 'desc' in header_lower or '설명' in header_lower or 'description' in header_lower:
                header_map['description'] = idx
        
        print(f"📋 헤더 매핑: {header_map}")
        
        # 데이터 추출
        data = []
        for row in all_values[1:]:  # 첫 번째 행(헤더) 제외
            if not row or len(row) == 0:
                continue
            
            table_name = row[header_map.get('table_name', 0)] if header_map.get('table_name') is not None and len(row) > header_map.get('table_name', 0) else ""
            columns = row[header_map.get('columns', 1)] if header_map.get('columns') is not None and len(row) > header_map.get('columns', 1) else ""
            description = row[header_map.get('description', 2)] if header_map.get('description') is not None and len(row) > header_map.get('description', 2) else ""
            
            if table_name:  # 빈 행 건너뛰기
                data.append({
                    "table_name": table_name,
                    "columns": columns,
                    "description": description
                })
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ Google Sheets에서 데이터 가져오기 실패: {e}")
        return None

def build_rag_index():
    # 1. Excel 파일이 있으면 Excel에서 읽기
    if EXCEL_PATH and os.path.exists(EXCEL_PATH):
        print(f"📊 Excel 파일에서 데이터 읽기: {EXCEL_PATH}")
        df = pd.read_excel(EXCEL_PATH, sheet_name="TABLE_SUMMARY")
    # 2. Google Sheets에서 읽기
    elif GOOGLE_SHEETS_CREDENTIALS_PATH and GOOGLE_SHEETS_SPREADSHEET_ID:
        print(f"📊 Google Sheets에서 데이터 읽기...")
        df = get_data_from_google_sheets()
        if df is None or df.empty:
            print("❌ 데이터를 가져올 수 없습니다.")
            return
    else:
        print("❌ Excel 파일 경로(EXCEL_PATH) 또는 Google Sheets 설정이 필요합니다.")
        print("   .env 파일에 다음 중 하나를 설정하세요:")
        print("   - EXCEL_PATH=path/to/file.xlsx")
        print("   - GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json")
        print("   - GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id")
        return

    print(f"✅ {len(df)}개의 테이블 정보를 찾았습니다.")
    print("🔄 임베딩 생성 중...")

    rag_list = []

    for idx, row in df.iterrows():
        table = row["table_name"]
        columns = row["columns"]
        desc = row["description"]

        if not table:  # 빈 행 건너뛰기
            continue

        text_block = f"""
Table: {table}
Columns: {columns}
Description: {desc}
""".strip()

        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=text_block
        ).data[0].embedding

        rag_list.append({
            "table_name": table,
            "text": text_block,
            "embedding": emb
        })
        
        print(f"  [{idx+1}/{len(df)}] {table} 완료")

    # 현재 디렉토리에 저장
    output_path = os.path.join(os.getcwd(), OUTPUT_JSON)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rag_list, f, ensure_ascii=False, indent=2)

    print(f"✅ rag_index.json 생성 완료: {output_path}")
    print(f"   총 {len(rag_list)}개의 테이블 임베딩이 생성되었습니다.")


if __name__ == "__main__":
    build_rag_index()
