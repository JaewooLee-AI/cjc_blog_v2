import time
import random
import os
import sys
import json
import re
from playwright.sync_api import sync_playwright
import clipboard_manager
import db_manager

STATE_FILE = os.path.join(os.path.dirname(__file__), "naver_state.json")
STATUS_FILE = os.path.join(os.path.dirname(__file__), "paste_status.json")

def human_delay(min_sec: float = 0.1, max_sec: float = 0.3):
    time.sleep(random.uniform(min_sec, max_sec))

def write_status(status: str, message: str):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"status": status, "message": message, "time": time.time()}, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing status file: {e}")

def ensure_clean_editor_state(editor_frame):
    """
    네이버 스마트에디터 ONE의 '작성 중인 글이 있습니다' 팝업을 감지하여
    [취소] 버튼을 자동 클릭해 항상 깨끗한 '새 글 작성' 상태로 초기화합니다.
    """
    print("Checking for draft restore popups...")
    cancel_selectors = [
        ".se-popup-button-cancel",
        "button.se-popup-button-cancel",
        ".se-popup-button.se-popup-button-cancel",
        ".se-help-panel-close-button",
        "button:has-text('취소')",
        "button:has-text('아니오')",
        ".se-popup-container button:nth-child(1)"
    ]
    for _ in range(12):
        try:
            for sel in cancel_selectors:
                cancel_btn = editor_frame.query_selector(sel)
                if cancel_btn and cancel_btn.is_visible():
                    cancel_btn.click(force=True)
                    print("Successfully auto-clicked [취소] on Naver draft restore popup!")
                    human_delay(1.0, 1.5) # 팝업 닫힘 및 캔버스 초기화 완전 대기
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

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

def upload_single_photo(page, editor_frame, file_path: str) -> bool:
    """단일 실사 이미지 1장을 네이버 스마트에디터 ONE의 지정 커서 위치에 개별 업로드 (콜라주/슬라이드 팝업 방지)"""
    photo_selectors = [
        "button.se-image-toolbar-button",
        "button.se-document-toolbar-image-button",
        "button[data-name='image']",
        ".se-toolbar-button-image",
        ".se-toolbar-item-image button",
        "button:has-text('사진')",
        ".se-image-toolbar-button button"
    ]
    photo_btn = None
    for sel in photo_selectors:
        try:
            el = editor_frame.query_selector(sel)
            if el and el.is_visible():
                photo_btn = el
                break
        except Exception:
            pass

    if photo_btn:
        try:
            with page.expect_file_chooser(timeout=3000) as fc_info:
                photo_btn.click(force=True)
            file_chooser = fc_info.value
            file_chooser.set_files([file_path])
            human_delay(1.5, 2.5) # 개별 사진 네이버 CDN 업로드 대기
            return True
        except Exception as e:
            print(f"File chooser single photo upload error: {e}")

    # 폴백: direct input[type="file"]
    try:
        file_inputs = editor_frame.query_selector_all('input[type="file"]')
        if file_inputs:
            file_inputs[0].set_input_files([file_path])
            human_delay(1.5, 2.5)
            return True
    except Exception as e:
        print(f"Direct file_input single photo error: {e}")

    return False

def select_and_focus_marker(editor_frame, page, marker_str: str) -> bool:
    """
    네이버 스마트에디터 ONE DOM 내에서 마커 텍스트 노드를 찾아
    정확히 해당 단락 위치로 스크롤 및 커서 포커스를 100% 고정한 뒤 마커 텍스트 삭제
    """
    try:
        # JS TreeWalker로 exact marker_str을 포함하는 텍스트 노드 탐색 및 텍스트 선택(Selection) 설정
        found = editor_frame.evaluate("""(markerText) => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
            let node;
            while (node = walker.nextNode()) {
                if (node.nodeValue && node.nodeValue.includes(markerText)) {
                    let parent = node.parentElement;
                    while (parent && !parent.classList.contains('se-text-paragraph') && parent.tagName !== 'P' && parent.tagName !== 'DIV') {
                        parent = parent.parentElement;
                    }
                    const targetEl = parent || node.parentElement;
                    targetEl.scrollIntoView({ behavior: 'auto', block: 'center' });
                    
                    const range = document.createRange();
                    range.selectNodeContents(targetEl);
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                    return true;
                }
            }
            return false;
        }""", marker_str)

        if found:
            print(f"✅ Successfully located and focused marker '{marker_str}' via DOM Selection API!")
            human_delay(0.2, 0.4)
            page.keyboard.press("Backspace")
            human_delay(0.4, 0.6)
            return True
        else:
            print(f"⚠️ Could not find marker '{marker_str}' via JS TreeWalker")
            return False
    except Exception as e:
        print(f"select_and_focus_marker error for '{marker_str}': {e}")
        return False

def run_worker():
    if len(sys.argv) < 4:
        write_status("ERROR", "Invalid arguments passed to worker.")
        return

    blog_id = sys.argv[1].strip()
    title = sys.argv[2]
    content_file = sys.argv[3]

    if not os.path.exists(content_file):
        write_status("ERROR", f"Content file not found: {content_file}")
        return

    image_paths = []
    try:
        with open(content_file, "r", encoding="utf-8") as f:
            raw_data = f.read()
            if raw_data.strip().startswith("{"):
                post_json = json.loads(raw_data)
                html_content = post_json.get("content", "")
                image_paths = post_json.get("image_paths", [])
            else:
                html_content = raw_data
    except Exception as e:
        write_status("ERROR", f"Failed to read content file: {e}")
        return

    print(f"📷 Available images to upload: {len(image_paths) if image_paths else 0}")

    # 마커 생성 함수: html_content 내 <img> 태그들을 top-to-bottom 순서대로 고유 마커로 단 1회 통합 치환
    marker_counter = [0]
    def replace_with_marker(match):
        marker_counter[0] += 1
        return f'<p style="color: #888888; text-align: center; font-size: 14px; margin: 15px 0;">[📷 PHOTO_LOCATION_MARKER_{marker_counter[0]}]</p>'

    combined_pattern = r'(?:<br\s*/?>\s*)?(?:<div[^>]*>\s*)?<img\s+[^>]*?src=["\'][^"\']+["\'][^>]*?>(?:\s*<p[^>]*>.*?</p>)?(?:\s*</div>)?(?:\s*<br\s*/?>)?'
    clean_text_html = re.sub(combined_pattern, replace_with_marker, html_content, flags=re.IGNORECASE | re.DOTALL)

    print(f"Total markers created: {marker_counter[0]}")
    print(f"Total images to upload: {len(image_paths) if image_paths else 0}")

    # 정제된 텍스트 본문을 클립보드에 바인딩
    clipboard_manager.copy_html_to_clipboard(clean_text_html, for_word=False)

    state_option = {}
    if os.path.exists(STATE_FILE):
        state_option["storage_state"] = STATE_FILE

    target_url = f"https://blog.naver.com/{blog_id}?Redirect=Write"

    write_status("RUNNING", "Launching Chromium browser...")

    with sync_playwright() as p:
        try:
            browser = launch_browser(p, headless=False)
            context = browser.new_context(viewport={"width": 1280, "height": 900}, **state_option)
            page = context.new_page()
            page.on("dialog", lambda dialog: dialog.accept())

            page.goto(target_url, wait_until="domcontentloaded")
            human_delay(1.0, 1.5)

            if "nidlogin" in page.url:
                write_status("LOGIN_REQUIRED", "🔑 네이버 로그인 세션이 만료되었습니다. 먼저 로그인을 완료해 주세요!")
                # 로그인 완료 대기
                for _ in range(60):
                    if page.is_closed() or "nidlogin" not in page.url:
                        break
                    time.sleep(1)
                try:
                    context.storage_state(path=STATE_FILE)
                except Exception:
                    pass

            editor_frame = page
            try:
                frame = page.frame(name="mainFrame")
                if not frame:
                    page.wait_for_selector("#mainFrame", timeout=4000)
                    frame = page.frame(name="mainFrame")
                if frame:
                    editor_frame = frame
            except Exception:
                editor_frame = page

            # 5. 임시저장 팝업 감지 시 [취소]를 자동 클릭하여 깨끗한 '새 글 작성' 상태로 강제 초기화
            ensure_clean_editor_state(editor_frame)

            # 제목 입력
            modifier = "Meta" if sys.platform == "darwin" else "Control"
            try:
                # 제목 텍스트 정제 (HTML 태그 및 [SEO 정보] 제거)
                clean_title = re.sub(r"<[^>]+>", "", title).strip()
                clean_title = re.sub(r"^\[SEO 정보\]\s*", "", clean_title).strip()
                print(f"Executing title auto-fill into Title Field: {clean_title}")

                # 제목 필드 찾기 및 클릭
                title_selectors = [
                    ".se-component-title .se-text-paragraph",
                    ".se-document-title .se-text-paragraph",
                    ".se-title-text",
                    "div.se-component-title p",
                    ".se-document-title-container"
                ]

                title_el = None
                for sel in title_selectors:
                    try:
                        el = editor_frame.query_selector(sel)
                        if el and el.is_visible():
                            title_el = el
                            print(f"Found title field with selector: {sel}")
                            break
                    except Exception:
                        pass

                if title_el:
                    # 제목 필드 클릭 및 내용 지우기
                    title_el.click(force=True)
                    human_delay(0.3, 0.5)

                    # 기존 텍스트 선택 및 삭제
                    page.keyboard.press(f"{modifier}+a")
                    human_delay(0.1, 0.2)
                    page.keyboard.press("Backspace")
                    human_delay(0.2, 0.3)

                    # 제목 입력
                    page.keyboard.type(clean_title, delay=15)
                    human_delay(0.4, 0.6)

                    print(f"Successfully typed title into field: {clean_title}")

                    # 제목 입력 후 본문 영역으로 이동 준비
                    body_el = editor_frame.query_selector(".se-main-container, .se-component-text, .se-content")
                    if body_el:
                        body_el.click(force=True)
                        human_delay(0.4, 0.6)
                else:
                    print("Warning: Could not find title field with any selector")

            except Exception as e:
                print(f"Title input error: {e}")

            # 본문 붙여넣기
            try:
                # 본문 영역 찾기
                body_el = editor_frame.query_selector(".se-main-container, .se-component-text, .se-content, .se-module-text")
                if body_el:
                    body_el.click(force=True)
                    human_delay(0.5, 0.8)

                    # 기존 내용 전체 선택 및 삭제 (취소선 방지)
                    page.keyboard.press(f"{modifier}+a")
                    human_delay(0.2, 0.4)
                    page.keyboard.press("Delete")
                    human_delay(0.2, 0.4)
                    page.keyboard.press("Backspace")
                    human_delay(0.2, 0.4)

                    # 새로운 내용 붙여넣기
                    page.keyboard.press(f"{modifier}+v")
                    human_delay(1.0, 1.5)
                else:
                    # 본문 영역을 못 찾은 경우 그냥 붙여넣기 시도
                    page.keyboard.press(f"{modifier}+v")
                    human_delay(1.0, 1.5)
            except Exception as e:
                print(f"Body paste error: {e}")

            # 네이버 스마트에디터 ONE 미리보기 위치(마커) 100% 일치 실사 사진 개별 자동 첨부
            if image_paths:
                abs_valid_paths = [os.path.abspath(p) for p in image_paths if os.path.exists(os.path.abspath(p))]
                if abs_valid_paths:
                    print(f"Uploading {len(abs_valid_paths)} photos at 100% exact preview marker positions...")
                    
                    for img_idx, single_path in enumerate(abs_valid_paths, 1):
                        marker_str = f"[📷 PHOTO_LOCATION_MARKER_{img_idx}]"
                        print(f"Locating exact marker '{marker_str}' for photo #{img_idx}/{len(abs_valid_paths)}...")

                        focused = select_and_focus_marker(editor_frame, page, marker_str)
                        if not focused:
                            print(f"Falling back to Playwright query selector for marker '{marker_str}'...")
                            all_p = editor_frame.query_selector_all("p, .se-text-paragraph, .se-component-text p")
                            for p in all_p:
                                try:
                                    if marker_str in p.inner_text():
                                        p.scroll_into_view_if_needed()
                                        p.click(click_count=3, force=True)
                                        human_delay(0.2, 0.3)
                                        page.keyboard.press("Backspace")
                                        human_delay(0.4, 0.6)
                                        focused = True
                                        break
                                except Exception:
                                    pass

                        print(f"Uploading single photo #{img_idx} at exact marker location...")
                        upload_success = upload_single_photo(page, editor_frame, single_path)
                        if upload_success:
                            print(f"✅ Photo #{img_idx} uploaded successfully at marker location!")
                        else:
                            print(f"❌ Photo #{img_idx} upload failed")

            # DB 적재
            db_manager.save_post_log(
                post_type="NAVER_SEMI_AUTO",
                title=title,
                content=html_content,
                status="WAITING_FOR_USER_PUBLISH",
                target_url=target_url
            )

            # 붙여넣기 즉시 성공 상태 알림
            write_status("SUCCESS", "✅ 네이버 스마트에디터 ONE에 제목과 본문 입력이 완료되었습니다! 크롬 창에서 [발행] 버튼을 눌러주세요.")

            # 백그라운드에서 사용자가 창을 닫을 때까지 크롬 유지
            print("Keeping browser open for user interaction (will auto-close when window is closed)...")
            for i in range(300):
                try:
                    if page.is_closed() or len(context.pages) == 0:
                        print(f"Browser window closed by user at iteration {i}")
                        break
                except Exception:
                    print(f"Browser connection lost at iteration {i}")
                    break
                time.sleep(1)
            print("Browser monitoring loop finished, closing browser...")

        except Exception as ex:
            write_status("ERROR", f"에디터 전송 중 오류 발생: {ex}")
        finally:
            # 브라우저 명시적 종료 (중요: Dock에 크롬 쌓이는 문제 해결)
            try:
                if 'browser' in locals() and browser is not None:
                    print("Explicitly closing browser to prevent memory leaks...")
                    browser.close()
                    print("Browser closed successfully")
            except Exception as close_err:
                print(f"Browser close note: {close_err}")

            print("Paste worker process terminating...")

if __name__ == "__main__":
    run_worker()
