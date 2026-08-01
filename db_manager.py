import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cjc_blog.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """SQLite 데이터베이스 및 테이블 초기화"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 크롤링 뉴스/트렌드 중복 확인용 테이블 (O(1) 해시 비교)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            source TEXT,
            crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. 블로그 생성 및 전송 이력 적재용 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'CREATED',
            target_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. 실사 이미지 라이브러리 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT '일반',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def normalize_url(url: str) -> str:
    """구글 RSS 및 뉴스 트래킹 파라미터(oc, hl, gl, utm_*)를 제거하여 정제된 URL 생성"""
    if not url:
        return ""
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(url.strip())
        qd = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        drop_keys = {"oc", "hl", "gl", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ved", "usg"}
        clean_qd = {k: v for k, v in qd.items() if k.lower() not in drop_keys}
        clean_query = urllib.parse.urlencode(clean_qd, doseq=True)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, clean_query, parsed.fragment))
    except Exception:
        return url.strip()

def hash_url(url: str) -> str:
    """정규화된 URL을 SHA256 해시 문자열로 변환하여 O(1) 키 생성"""
    clean_url = normalize_url(url).lower()
    return hashlib.sha256(clean_url.encode('utf-8')).hexdigest()

def hash_title(title: str) -> str:
    """기사 제목 특수문자 및 공백 제거 후 SHA256 해시 생성 (동일 기사의 리다이렉트 URL 차단)"""
    import re
    clean_t = re.sub(r'[\s\W]+', '', title.strip().lower())
    return hashlib.sha256(clean_t.encode('utf-8')).hexdigest()

def is_article_exists(url: str, title: str = "") -> bool:
    """해당 URL 또는 기사 제목이 이미 크롤링되어 DB에 존재하는지 O(1) 해시 비교 검사"""
    url_h = hash_url(url)
    conn = get_connection()
    cursor = conn.cursor()
    
    if title and len(title.strip()) > 5:
        # URL 해시 또는 제목 단순 비교
        cursor.execute("SELECT 1 FROM article_history WHERE url_hash = ? OR title = ?", (url_h, title.strip()))
    else:
        cursor.execute("SELECT 1 FROM article_history WHERE url_hash = ?", (url_h,))
        
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_article_history(url: str, title: str, source: str = "RSS") -> bool:
    """크롤링된 기사 URL 및 메타데이터 저장"""
    url_h = hash_url(url)
    if is_article_exists(url, title):
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO article_history (url_hash, url, title, source) VALUES (?, ?, ?, ?)",
            (url_h, normalize_url(url), title.strip(), source)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_recent_articles_for_dedup(limit: int = 30) -> list:
    """2차 LLM 시맨틱 중복 검증의 대조군으로 활용할 최근 수집 기사 목록 반환"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url, title, source, crawled_at
            FROM article_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"url": r[0], "title": r[1], "summary": r[1], "source": r[2]} for r in rows]
    except Exception as e:
        print(f"get_recent_articles_for_dedup error: {e}")
        return []

def clear_article_history() -> int:
    """수집된 기사 중복 방지 이력 테이블(article_history)을 초기화하여 테스트 시 재수집 가능하게 처리"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM article_history")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def save_post_log(post_type: str, title: str, content: str, status: str = "CREATED", target_url: str = "") -> int:
    """원고 생성 및 발행 이력 저장"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO post_logs (post_type, title, content, status, target_url) VALUES (?, ?, ?, ?, ?)",
        (post_type, title, content, status, target_url)
    )
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def get_recent_logs(limit: int = 50):
    """최근 생성/발행된 원고 로그 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, post_type, title, status, created_at FROM post_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_article_history(limit: int = 50):
    """최근 수집된 기사 이력 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, source, url, crawled_at FROM article_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_image_metadata(filename: str, filepath: str, description: str, category: str = "일반") -> int:
    """실사 이미지 메타데이터 저장"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO image_library (filename, filepath, description, category) VALUES (?, ?, ?, ?)",
        (filename, filepath, description, category)
    )
    img_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return img_id

def get_all_images() -> list:
    """등록된 모든 실사 이미지 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, filepath, description, category, created_at FROM image_library ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    images = []
    for r in rows:
        images.append({
            "id": r[0],
            "filename": r[1],
            "filepath": r[2],
            "description": r[3],
            "category": r[4],
            "created_at": r[5]
        })
    return images

def delete_image(image_id: int) -> bool:
    """이미지 DB 레코드 삭제 및 실물 파일 제거"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM image_library WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        filepath = row[0]
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"File remove error: {e}")
        cursor.execute("DELETE FROM image_library WHERE id = ?", (image_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def update_image_metadata(image_id: int, description: str = None, category: str = None) -> bool:
    """기존 이미지의 메타데이터 업데이트 (설명, 카테고리)"""
    conn = get_connection()
    cursor = conn.cursor()

    # 업데이트할 필드만 동적으로 구성
    update_fields = []
    params = []

    if description is not None:
        update_fields.append("description = ?")
        params.append(description)

    if category is not None:
        update_fields.append("category = ?")
        params.append(category)

    if not update_fields:
        conn.close()
        return False

    params.append(image_id)  # WHERE 조건용 파라미터

    query = f"UPDATE image_library SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, params)

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows > 0

def clear_all_logs() -> bool:
    """포스팅 이력, 크롤링 아카이빙 DB 테이블 및 CSV 로그 파일 1클릭 초기화"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post_logs")
    cursor.execute("DELETE FROM article_history")
    conn.commit()
    conn.close()

    csv_path = os.path.join(os.path.dirname(__file__), "cjc_blog_logs.csv")
    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception as e:
            print(f"CSV log remove error: {e}")
    return True

def get_dashboard_stats() -> dict:
    """대시보드 KPI 메트릭 및 통계용 데이터 집계"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM post_logs")
    total_posts = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM post_logs WHERE status IN ('SUCCESS', 'WAITING_FOR_USER_PUBLISH', 'NAVER_SEMI_AUTO')")
    naver_published = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM article_history")
    archived_articles = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM image_library")
    total_images = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_posts": total_posts,
        "naver_published": naver_published,
        "archived_articles": archived_articles,
        "total_images": total_images
    }

def get_all_post_logs(limit: int = 200) -> list:
    """포스팅 로그 전체 상세 이력 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, post_type, title, content, status, target_url, created_at FROM post_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "post_type": r[1],
            "title": r[2],
            "content": r[3],
            "status": r[4],
            "target_url": r[5],
            "created_at": r[6]
        })
    return logs

# 모듈 로드시 DB 자동 초기화
init_db()
