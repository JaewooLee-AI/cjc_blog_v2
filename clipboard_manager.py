import sys
import os
import subprocess
import re
import pathlib
import hashlib

def prepare_html_for_clipboard(html_content: str) -> str:
    """
    MS Word, 한글(HWP), 네이버 스마트에디터 호환성을 위해
    HTML 내 data:image/png;base64,... 형태의 인라인 이미지를 로컬 file:///... URI 경로로 변환.
    """
    if not html_content or "data:image" not in html_content:
        return html_content

    cache_dir = os.path.join(os.path.dirname(__file__), "uploaded_images", "clipboard_cache")
    os.makedirs(cache_dir, exist_ok=True)

    def replace_b64(match):
        ext = match.group(1).lower()
        if ext == "jpeg":
            ext = "jpg"
        b64_data = match.group(2)
        try:
            h = hashlib.md5(b64_data.encode('utf-8')).hexdigest()[:10]
            fname = f"clip_{h}.{ext}"
            fpath = os.path.join(cache_dir, fname)
            if not os.path.exists(fpath):
                import base64
                with open(fpath, "wb") as f:
                    f.write(base64.b64decode(b64_data))
            file_uri = pathlib.Path(fpath).as_uri()
            return f'src="{file_uri}"'
        except Exception as e:
            print(f"B64 to file URI conversion error: {e}")
            return match.group(0)

    pattern = r'src=[\"\']data:image/(png|jpeg|jpg|webp);base64,([^\'\"]+)[\"\']'
    return re.sub(pattern, replace_b64, html_content)

def copy_html_to_clipboard(html_content: str, for_word: bool = False) -> bool:
    """
    HTML 콘텐츠를 OS 시스템 클립보드에 바인딩하는 크로스플랫폼 핸들러.
    - for_word=True: MS Word / 한글(HWP)용 (Base64 -> file:///... 경로 변환)
    - for_word=False: 네이버 스마트에디터 ONE 전용 (Base64 data:image/png 인라인 이미지 유지)
    """
    if for_word:
        html_content = prepare_html_for_clipboard(html_content)

    # 1. Windows 환경
    if sys.platform.startswith("win"):
        try:
            import win32clipboard
            
            # CF_HTML 규격 바이트 헤더 작성
            MARKER_BLOCK = (
                "Version:0.9\r\n"
                "StartHTML:{:08d}\r\n"
                "EndHTML:{:08d}\r\n"
                "StartFragment:{:08d}\r\n"
                "EndFragment:{:08d}\r\n"
            )
            HTML_HEADER = "<html><body><!--StartFragment-->"
            HTML_FOOTER = "<!--EndFragment--></body></html>"
            
            dummy_header = MARKER_BLOCK.format(0, 0, 0, 0)
            start_html = len(dummy_header)
            start_fragment = start_html + len(HTML_HEADER)
            end_fragment = start_fragment + len(html_content.encode('utf-8'))
            end_html = end_fragment + len(HTML_FOOTER)
            
            header = MARKER_BLOCK.format(start_html, end_html, start_fragment, end_fragment)
            full_payload = (header + HTML_HEADER + html_content + HTML_FOOTER).encode('utf-8')
            
            cf_html_id = win32clipboard.RegisterClipboardFormat("HTML Format")
            win32clipboard.OpenClipboard(0)
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(cf_html_id, full_payload)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"Windows win32clipboard error: {e}")
            
    # 2. macOS 환경 (osascript «class HTML» 로 OS 클립보드에 리치 HTML 포맷 직접 바인딩)
    elif sys.platform == "darwin":
        try:
            hex_data = html_content.encode('utf-8').hex()
            applescript = f'set the clipboard to {{«class HTML»:«data HTML{hex_data}»}}'
            proc = subprocess.Popen(['osascript', '-e', applescript], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()
            return True
        except Exception as e:
            print(f"macOS osascript HTML clipboard error: {e}")
            try:
                import pyperclip
                pyperclip.copy(html_content)
                return True
            except Exception:
                pass
            
    # 3. 기타 범용 (pyperclip)
    try:
        import pyperclip
        pyperclip.copy(html_content)
        return True
    except Exception as e:
        print(f"Fallback pyperclip error: {e}")
        return False
