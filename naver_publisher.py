import time
import random
import os
import sys
import json
import subprocess
from typing import Dict, Any
from playwright.sync_api import sync_playwright

STATE_FILE = os.path.join(os.path.dirname(__file__), "naver_state.json")
STATUS_FILE = os.path.join(os.path.dirname(__file__), "paste_status.json")

def human_delay(min_sec: float = 0.1, max_sec: float = 0.3):
    """네이버 안티 봇 탐지 우회를 위한 인간 유사 랜덤 지연 메커니즘"""
    time.sleep(random.uniform(min_sec, max_sec))

def launch_browser(p, headless: bool = False, args: list = None):
    """macOS Crashpad 및 Mach Port 권한 충돌 방지를 위한 안전 브라우저 구동 모듈"""
    if args is None:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        if not sys.platform.startswith("darwin"):
            args.extend(["--no-sandbox", "--disable-dev-shm-usage"])
    else:
        if sys.platform.startswith("darwin"):
            args = [a for a in args if a not in ["--no-sandbox", "--disable-dev-shm-usage"]]

    # 1차 시도: macOS 정식 Google Chrome 앱 경로 (/Applications/Google Chrome.app)
    chrome_app_mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if sys.platform == "darwin" and os.path.exists(chrome_app_mac):
        try:
            return p.chromium.launch(headless=headless, executable_path=chrome_app_mac, args=args)
        except Exception as e:
            print(f"System Chrome path launch fallback: {e}")

    # 2차 시도: channel="chrome"
    try:
        return p.chromium.launch(headless=headless, channel="chrome", args=args)
    except Exception as e:
        print(f"System Chrome channel launch fallback: {e}")

    # 3차 시도: 번들 Chromium
    return p.chromium.launch(headless=headless, args=args)

def open_naver_login_session(blog_id: str = "") -> Dict[str, Any]:
    """
    네이버 로그인 세션 획득 및 naver_state.json 저장 모듈.
    프로필 오염 없이 깔끔하게 쿠키(NID_AUT/NID_SES)만 추출하여 JSON으로 안전 저장.
    """
    clean_id = blog_id.strip()
    target_url = f"https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fblog.naver.com%2F{clean_id}%3FRedirect%3DWrite" if clean_id else "https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fsection.blog.naver.com"
    
    with sync_playwright() as p:
        print("Launching clean Playwright Chrome for Naver login...")
        browser = launch_browser(p, headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(target_url, wait_until="domcontentloaded")
        
        print("Waiting for Naver login authentication cookies (NID_AUT, NID_SES)...")
        logged_in = False
        for _ in range(120):
            try:
                if page.is_closed():
                    break
                cookies = context.cookies()
                has_auth = any(c.get('name') in ['NID_AUT', 'NID_SES'] for c in cookies)
                
                if has_auth:
                    human_delay(2.0, 3.0)
                    context.storage_state(path=STATE_FILE)
                    print(f"Successfully saved Naver login session to {STATE_FILE}")
                    logged_in = True
                    break
            except Exception:
                break
            time.sleep(1)
            
        browser.close()
        
        if logged_in and os.path.exists(STATE_FILE):
            return {
                "success": True,
                "message": "🔑 네이버 패스키 / OTP 로그인 인증이 성공하여 세션이 naver_state.json 파일에 영구 저장되었습니다! 이제 원고 전송을 바로 진행해 주세요."
            }
        else:
            if os.path.exists(STATE_FILE):
                try:
                    os.remove(STATE_FILE)
                except Exception:
                    pass
            return {
                "success": False,
                "message": "⚠️ 네이버 로그인이 완료되지 않은 상태에서 브라우저가 닫혔습니다. 패스키/OTP/비밀번호 로그인을 끝까지 마쳐주세요!"
            }

def open_naver_smart_editor(title: str, html_content: str, blog_id: str = "", image_paths: list = None) -> Dict[str, Any]:
    """
    백그라운드 비동기 워커(paste_worker.py)를 구동하여 
    Streamlit UI 스피너를 2~3초 만에 깔끔하게 해제하고, 크롬 브라우저를 독립 유지시키는 모듈.
    """
    clean_blog_id = blog_id.strip()
    if not clean_blog_id:
        return {
            "success": False,
            "message": "⚠️ 네이버 블로그 아이디가 입력되지 않았습니다. 좌측 사이드바에서 블로그 아이디를 입력해 주세요!"
        }

    # 1. 원고 및 이미지 경로 데이터 바인딩 (JSON)
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_posts")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "current_post.json")
    post_data = {
        "title": title,
        "content": html_content,
        "image_paths": image_paths or []
    }
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)

    # 이전 상태 파일 초기화
    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
        except Exception:
            pass

    # 2. 백그라운드 워커 프로세스 독립 생성 (Streamlit 웹 UI 즉시 해제!)
    worker_script = os.path.join(os.path.dirname(__file__), "paste_worker.py")
    python_exe = sys.executable
    
    print(f"Launching paste_worker.py asynchronously in background for blog: {clean_blog_id}...")
    subprocess.Popen([python_exe, worker_script, clean_blog_id, title, temp_file])

    # 3. 붙여넣기 완료 응답 감지 (최대 10초, 완료 시 2~3초 만에 즉시 스피너 해제!)
    for _ in range(25): # 0.4s * 25 = 10s
        time.sleep(0.4)
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                status = sdata.get("status")
                message = sdata.get("message", "")

                if status == "SUCCESS":
                    return {
                        "success": True,
                        "message": message
                    }
                elif status in ["ERROR", "LOGIN_REQUIRED"]:
                    return {
                        "success": False,
                        "message": message
                    }
            except Exception:
                pass

    return {
        "success": True,
        "message": "✅ 네이버 스마트에디터 ONE 원고 전송 프로세스가 백그라운드에서 구동되었습니다! 열려 있는 크롬 창에서 [발행] 버튼을 눌러주세요."
    }
