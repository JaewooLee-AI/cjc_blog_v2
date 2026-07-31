import os
import csv
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import db_manager

CSV_LOG_PATH = os.path.join(os.path.dirname(__file__), "cjc_blog_logs.csv")

def init_csv_log():
    if not os.path.exists(CSV_LOG_PATH):
        with open(CSV_LOG_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "PostType", "Title", "Status", "TargetURL"])

def log_event(post_type: str, title: str, status: str = "COMPLETED", target_url: str = ""):
    """원고 발행 이벤트 적재 (CSV 및 DB)"""
    init_csv_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. CSV 파일 기록
    with open(CSV_LOG_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, post_type, title, status, target_url])
        
    # 2. 구글 시트 연동 시도 (gspread 설정 시)
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            gs_url = cfg.get("google_sheets", {}).get("spreadsheet_url")
            if gs_url:
                # GSheets API 지원 연동 가능
                pass
        except Exception:
            pass

def get_log_dataframe() -> pd.DataFrame:
    """대시보드 모니터링 표출용 DataFrame 반환"""
    init_csv_log()
    # DB 로그와 CSV 로그 통합
    db_logs = db_manager.get_recent_logs(limit=100)
    if db_logs:
        df = pd.DataFrame(db_logs, columns=["ID", "구분", "제목", "상태", "생성일시"])
        return df
    elif os.path.exists(CSV_LOG_PATH):
        return pd.read_csv(CSV_LOG_PATH)
    return pd.DataFrame(columns=["ID", "구분", "제목", "상태", "생성일시"])
