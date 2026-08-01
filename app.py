import streamlit as st
import json
import os
import pandas as pd
import time
from typing import Dict, Any, List, Optional

import io
import zipfile
import db_manager
import crawler
import llm_router
import naver_publisher
import logger
import clipboard_manager

# -----------------------------------------------------------------------------
# 1. 페이지 및 CSS 스타일 설정 (Rich Aesthetics Design System)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="씨제이씨협동조합 | AI 블로그 SEO & 포스팅 시스템",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<meta name="google" content="notranslate" />
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Pretendard:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .notranslate {
        translate: no;
    }

    /* Hide Streamlit default chrome headers */
    button[kind="header"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 21st.dev Glassmorphic Header Banner */
    .header-banner {
        position: relative;
        background: radial-gradient(120% 120% at 50% 0%, #1E1B4B 0%, #0F172A 50%, #020617 100%);
        color: #FFFFFF;
        padding: 32px 40px;
        border-radius: 20px;
        box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.15);
        margin-bottom: 28px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        overflow: hidden;
    }
    .header-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -20%;
        width: 140%;
        height: 200%;
        background: radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.18) 0%, transparent 40%),
                    radial-gradient(circle at 70% 80%, rgba(168, 85, 247, 0.15) 0%, transparent 40%);
        pointer-events: none;
    }
    .header-top-tag {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #A5B4FC;
        font-size: 12px;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
        letter-spacing: 0.5px;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }
    .header-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .header-subtitle {
        font-size: 15px;
        color: #94A3B8;
        margin-top: 8px;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Modern Tabs Styling (21st.dev Pill Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #64748B !important;
        padding: 0px 20px !important;
        border: none !important;
        background-color: transparent !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #4F46E5 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Modern Card Container */
    .cjc-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .cjc-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px -4px rgba(15, 23, 42, 0.1);
        border-color: #CBD5E1;
    }

    /* Modern Microcopy Callout Box */
    .microcopy-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
        border: 1px solid #A7F3D0;
        border-left: 4px solid #10B981;
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 14px;
        color: #064E3B;
        margin-bottom: 20px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.05);
    }
    .microcopy-box strong {
        color: #047857;
    }

    /* Modern Article Preview Box */
    .preview-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 28px;
        max-height: 520px;
        overflow-y: auto;
        box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.03);
    }

    /* Modern Streamlit Metric Cards (Glassmorphism look) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        padding: 18px 22px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        transition: all 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #6366F1;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #64748B !important;
        letter-spacing: -0.2px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }

    /* Modern Buttons Styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #334155 !important;
        font-weight: 600 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F8FAFC !important;
        border-color: #94A3B8 !important;
        color: #0F172A !important;
    }

    /* Sidebar Styling & High Contrast Crisp Input Elements */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #F1F5F9 !important;
    }
    section[data-testid="stSidebar"] input {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: #94A3B8 !important;
    }
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #312E81 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #6366F1 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Config 로드 및 상태 동기화
# -----------------------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config_data():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config_data(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config_data()

# 세션 스테이트 초기화
if "generated_article" not in st.session_state:
    st.session_state["generated_article"] = ""
if "generated_title" not in st.session_state:
    st.session_state["generated_title"] = ""
if "crawled_articles" not in st.session_state:
    st.session_state["crawled_articles"] = []

# -----------------------------------------------------------------------------
# 사이드바: 네이버 블로그 계정 글로벌 설정
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🟢 네이버 계정 설정")
    saved_blog_id = config.get("naver_settings", {}).get("naver_blog_id", "")
    active_blog_id = st.text_input(
        "네이버 블로그 아이디",
        value=saved_blog_id,
        placeholder="예: myblogid",
        help="네이버 글쓰기 페이지(https://blog.naver.com/아이디?Redirect=Write) 연결에 사용됩니다."
    )
    if active_blog_id.strip() != saved_blog_id:
        if "naver_settings" not in config:
            config["naver_settings"] = {}
        config["naver_settings"]["naver_blog_id"] = active_blog_id.strip()
        save_config_data(config)
        st.toast("네이버 블로그 아이디가 저장되었습니다!", icon="💾")
        
    st.divider()
    if st.button("🔑 네이버 패스키 로그인 등록", key="passkey_btn_sb", use_container_width=True, help="💡 클릭 시 브라우저가 열립니다. 네이버 패스키(Passkey), TouchID/생체인증, 혹은 QR 코드로 1회 로그인하면 세션이 영구 보관됩니다."):
        with st.spinner("네이버 패스키 로그인 창 구동 중... 브라우저에서 패스키/QR 로그인을 완료해 주세요!"):
            res = naver_publisher.open_naver_login_session(blog_id=active_blog_id.strip())
            st.success(res["message"])

# -----------------------------------------------------------------------------
# 3. 헤더 배너 표출 (21st.dev Glassmorphism Design)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <div class="header-top-tag">
        <span class="status-dot"></span> CJC COOPERATIVE AI ENGINE v2.5
    </div>
    <div class="header-title">씨제이씨협동조합 AI 블로그 SEO & 포스팅 시스템</div>
    <div class="header-subtitle">가발 산업 AX 디지털 대전환 | ATUM 3D 두상측정 & 키노피스(KINO PIECE) 브랜드 마케팅 자동화 솔루션</div>
</div>
""", unsafe_allow_html=True)

if "generated_image_paths" not in st.session_state:
    st.session_state["generated_image_paths"] = []

def create_image_zip(image_paths: list):
    valid_paths = [p for p in (image_paths or []) if os.path.exists(p)]
    if not valid_paths:
        return None
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, path in enumerate(valid_paths, 1):
            ext = os.path.splitext(path)[1]
            zf.write(path, f"cjc_photo_{idx}{ext}")
    buffer.seek(0)
    return buffer.getvalue()

def replace_nth_image_in_html(html: str, nth: int, new_src: str) -> str:
    """HTML 본문 내 N번째 (0-indexed) <img> 태그의 src 속성을 new_src로 위치 정확하게 치환"""
    import re
    pattern = r'(<img\s+[^>]*?src=["\'])([^"\']+)(["\'][^>]*?>)'
    matches = list(re.finditer(pattern, html, flags=re.IGNORECASE))
    
    if 0 <= nth < len(matches):
        match = matches[nth]
        start, end = match.span()
        full_match_text = match.group(0)
        updated_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{new_src}"', full_match_text, count=1, flags=re.IGNORECASE)
        return html[:start] + updated_tag + html[end:]
    return html

def delete_nth_image_in_html(html: str, nth: int) -> str:
    """HTML 본문 내 N번째 (0-indexed) <img> 태그 및 감싸고 있는 블록 삭제"""
    import re
    pattern = r'(<br\s*/?>\s*)?(<div\s+style="text-align:\s*center;[^"]*">\s*)?<img\s+[^>]*?src=["\'][^"\']+["\'][^>]*?>(\s*</div>)?(\s*<br\s*/?>)?'
    matches = list(re.finditer(pattern, html, flags=re.IGNORECASE))
    if 0 <= nth < len(matches):
        start, end = matches[nth].span()
        return html[:start] + html[end:]
    
    img_pattern = r'<img\s+[^>]*?src=["\'][^"\']+["\'][^>]*?>'
    img_matches = list(re.finditer(img_pattern, html, flags=re.IGNORECASE))
    if 0 <= nth < len(img_matches):
        start, end = img_matches[nth].span()
        return html[:start] + html[end:]
        
    return html


def clean_html_for_editor(html: str, image_paths: Optional[List[str]] = None) -> str:
    """HTML 본문 내의 거대한 Base64 Data URI (data:image/...;base64,...)를 깔끔한 파일 경로(src="uploaded_images/...")로 치환하여 편집기 텍스트 상자에 노출"""
    if not html:
        return ""
    
    import re
    image_paths = image_paths or []
    
    # Base64 src를 찾아서 순서대로 image_paths의 파일 경로로 교체
    pattern = r'src=["\']data:image/[^"\']+["\']'
    matches = list(re.finditer(pattern, html))
    
    clean_html = html
    for idx, match in reversed(list(enumerate(matches))):
        start, end = match.span()
        if idx < len(image_paths):
            path = image_paths[idx]
            clean_src = f'src="{path}"'
        else:
            clean_src = 'src="[CJC_IMAGE]"'
        clean_html = clean_html[:start] + clean_src + clean_html[end:]
        
    return clean_html

def restore_html_from_editor(html: str) -> str:
    """편집기에서 수정한 HTML 본문 내의 로컬 파일 경로(src="uploaded_images/...")를 렌더링 미리보기용 Base64 Data URI로 복원"""
    if not html:
        return ""
    
    import re, os
    pattern = r'src=["\']([^"\']+\.(?:png|jpg|jpeg|webp))["\']'
    matches = list(re.finditer(pattern, html, flags=re.IGNORECASE))
    
    restored_html = html
    for match in reversed(matches):
        start, end = match.span()
        file_path = match.group(1)
        if os.path.exists(file_path):
            b64_url = llm_router.get_image_src_url({"filepath": file_path})
            restored_html = restored_html[:start] + f'src="{b64_url}"' + restored_html[end:]
            
    return restored_html


# =============================================================================
# 3. SEO 포스팅 원고 미리보기, 수동 수정, 이미지 교체, LLM AI 재검토(Audit) 컴포넌트
# =============================================================================
def render_article_preview_and_editor(tab_key: str, active_blog_id: str):
    """3. 생성된 SEO 포스팅 원고 검수 및 미리보기, 수동 수정, 이미지 교체, LLM AI 재검토(Audit) 통합 컴포넌트"""
    if not st.session_state.get("generated_article"):
        st.info("👈 원고 생성을 진행하시면 본 영역에서 검수, 수동 수정, 이미지 교체 및 AI 재검토를 수행할 수 있습니다.")
        return

    key_editor = f"{tab_key}_edit_content_input"
    key_title = f"{tab_key}_edit_title_input"
    key_last_article = f"{tab_key}_last_synced_article"

    current_article = st.session_state.get("generated_article", "")
    current_title = st.session_state.get("generated_title", "")
    last_article = st.session_state.get(key_last_article, "")

    # 새로 원고가 생성되었거나 원고 내용이 변경되었으면 편집기 세션 값을 새 원고로 동기화!
    if current_article != last_article:
        st.session_state[key_last_article] = current_article
        st.session_state[key_editor] = clean_html_for_editor(
            current_article,
            st.session_state.get("generated_image_paths", [])
        )
        st.session_state[key_title] = current_title
        st.session_state.pop(f"{tab_key}_audit_result", None)

    if key_editor not in st.session_state:
        st.session_state[key_editor] = clean_html_for_editor(
            current_article,
            st.session_state.get("generated_image_paths", [])
        )
    if key_title not in st.session_state:
        st.session_state[key_title] = current_title

    st.markdown(f'<div class="notranslate" translate="no" style="margin-bottom: 10px;"><strong>📌 현재 글 제목:</strong> {st.session_state.get("generated_title", "")}</div>', unsafe_allow_html=True)
    
    # 🎯 [고도화 1] SEO 키워드 밀도 분석기 & AI 추천 해시태그 패키지 위젯
    seo_density = llm_router.analyze_seo_keyword_density(
        title=st.session_state.get("generated_title", ""),
        content_html=st.session_state.get("generated_article", "")
    )
    recommended_hashtags = llm_router.generate_recommended_hashtags(
        title=st.session_state.get("generated_title", ""),
        content_html=st.session_state.get("generated_article", "")
    )

    with st.expander("🎯 **SEO 키워드 밀도 분석기 & AI 추천 해시태그 패키지**", expanded=True):
        seo_col1, seo_col2, seo_col3 = st.columns([1.2, 1.2, 2.2])
        with seo_col1:
            st.metric("📝 총 단어 / 글자 수", f"{seo_density['total_words']}단어 / {seo_density['total_chars']}자")
        with seo_col2:
            st.metric("🎯 키워드 노출 횟수", f"{seo_density['total_keyword_matches']}회")
        with seo_col3:
            st.metric("📊 SEO 키워드 밀도", f"{seo_density['density_pct']}%", delta=seo_density['status_label'])

        # 키워드 밀도 보정 버튼
        if seo_density['status'] != "OPTIMAL":
            if st.button("⚡ 1클릭 SEO 키워드 자동 보정 (3~5% 최적 밀도 재구성)", key=f"{tab_key}_rebalance_btn", type="primary", use_container_width=True):
                with st.spinner("🤖 AI가 키워드 밀도를 3.0% ~ 5.0% 최적 범위로 재배치 보정 중입니다..."):
                    new_t, new_c, new_stats = llm_router.auto_rebalance_seo_keywords(
                        title=st.session_state.get("generated_title", ""),
                        content_html=st.session_state.get("generated_article", "")
                    )
                    st.session_state["generated_title"] = new_t
                    st.session_state["generated_article"] = new_c
                    st.session_state[key_title] = new_t
                    st.session_state[key_editor] = clean_html_for_editor(new_c, st.session_state.get("generated_image_paths", []))
                    st.session_state[key_last_article] = new_c
                    st.toast("⚡ SEO 키워드 밀도가 최적 범위로 자동 보정되었습니다!", icon="✨")
                    st.rerun()

        # AI 추천 해시태그 패키지
        st.markdown("##### 🏷️ AI 추천 상위 노출 해시태그 (네이버 발행 팝업용)")
        tag_str = " ".join(recommended_hashtags)
        st.text_input("추천 해시태그 목록", value=tag_str, key=f"{tab_key}_hashtag_input", help="네이버 블로그 [발행] 팝업창의 태그 입력 칸에 복사하여 붙여넣으세요.")
        
        if st.button("📋 해시태그 전체 1클릭 복사", key=f"{tab_key}_copy_tags_btn", use_container_width=True):
            clipboard_manager.copy_html_to_clipboard(tag_str)
            st.toast("📋 해시태그가 클립보드에 복사되었습니다! 네이버 [발행] 팝업에 붙여넣으세요.", icon="🏷️")

    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "👁️ 렌더링 미리보기",
        "✏️ 원고 수정 및 AI 재검토",
        "🖼️ 첨부 이미지 교체 및 삭제",
        "📄 HTML 소스 코드"
    ])

    # Sub-tab 1: 미리보기
    with sub_tab1:
        st.markdown(f'<div class="preview-box notranslate" translate="no">{st.session_state["generated_article"]}</div>', unsafe_allow_html=True)

    # Sub-tab 2: 원고 수동 수정 및 AI Audit
    with sub_tab2:
        st.markdown("##### ✏️ 제목 및 본문 수동 수정 / LLM AI 재검수")
        st.caption("제목과 본문을 직접 수정한 후, [🤖 수정한 원고 AI 재검토 요청]을 누르시면 SEO 점수, 가독성, 의료법/표시광고법 준수 여부를 AI가 자동 검수합니다.")
        
        edited_title = st.text_input(
            "📌 글 제목 수정",
            key=key_title
        )
        
        edited_content = st.text_area(
            "📝 본문 HTML/텍스트 수동 편집",
            height=320,
            key=key_editor
        )

        c_act1, c_act2 = st.columns([1, 1])
        with c_act1:
            if st.button("💾 수정사항 원고에 즉시 반영", key=f"{tab_key}_save_edit_btn", use_container_width=True):
                config = llm_router.load_config()
                sanitized_title = llm_router.sanitize_compliance(edited_title, config)
                sanitized_content = llm_router.sanitize_compliance(edited_content, config)
                restored_article = restore_html_from_editor(sanitized_content)
                st.session_state["generated_title"] = sanitized_title
                st.session_state["generated_article"] = restored_article
                st.session_state[key_last_article] = restored_article
                st.toast("💾 수정 내용이 원고에 반영되었습니다!", icon="✅")
                st.rerun()

        with c_act2:
            if st.button("🤖 수정한 원고 AI 재검토 요청", key=f"{tab_key}_audit_btn", type="primary", use_container_width=True):
                with st.spinner("🤖 LLM AI가 수정한 원고의 SEO/가독성/의료법 위반 여부를 종합 검수 중입니다..."):
                    audit_res = llm_router.audit_edited_article(edited_title, edited_content)
                    st.session_state[f"{tab_key}_audit_result"] = audit_res
                    st.toast("🤖 LLM AI 원고 검토가 완료되었습니다!", icon="✨")

        # Audit 결과 카드
        audit_res = st.session_state.get(f"{tab_key}_audit_result")
        if audit_res:
            st.divider()
            st.markdown("#### 📊 LLM AI 원고 재검토 분석 결과")
            
            kpi_col1, kpi_col2 = st.columns([1, 2])
            with kpi_col1:
                st.metric("종합 품질 점수", f"{audit_res.get('score', 85)}점 / 100점")
            with kpi_col2:
                if audit_res.get("compliance_pass"):
                    st.success("✅ 의료법 및 표시광고법 준수 검사 통과! (금지어 미발견)")
                else:
                    st.warning("⚠️ 과대광고/금지어 표현 포함 가능성 있음. 아래 추천을 확인하세요.")

            g_col, i_col = st.columns(2)
            with g_col:
                st.markdown("🟢 **잘된 점 (Good Points)**")
                for gp in audit_res.get("good_points", []):
                    st.write(f"- {gp}")
            with i_col:
                st.markdown("🟡 **개선 추천 및 리스크 (Improvements)**")
                for imp in audit_res.get("improvements", []):
                    st.write(f"- {imp}")

            if audit_res.get("suggested_title") or audit_res.get("suggested_content"):
                st.markdown("##### ✨ AI 추천 최적화 교정안")
                st.caption(f"**추천 제목:** {audit_res.get('suggested_title', '')}")
                if st.button("✨ AI 추천 교정 원고 1클릭 반영", key=f"{tab_key}_apply_audit_btn", type="primary", use_container_width=True):
                    restored_suggested = restore_html_from_editor(audit_res.get("suggested_content", edited_content))
                    suggested_title = audit_res.get("suggested_title", edited_title)
                    st.session_state["generated_title"] = suggested_title
                    st.session_state["generated_article"] = restored_suggested
                    # 다음 rerun 시 상단에서 widget 생성 전에 키를 갱신하도록 동기화 마커 초기화
                    st.session_state[key_last_article] = ""
                    st.toast("✨ AI 교정 원고로 1클릭 업데이트되었습니다!", icon="🚀")
                    st.rerun()

    # Sub-tab 3: 첨부 이미지 교체 및 삭제 (등록된 DB 이미지 전용)
    with sub_tab3:
        st.markdown("##### 🖼️ 등록된 실사 이미지 라이브러리 교체 및 삭제")
        all_db_images = db_manager.get_all_images()
        current_images = list(st.session_state.get("generated_image_paths", []))
        
        if not current_images:
            st.info("💡 현재 포스팅에 매핑된 실사 이미지가 없습니다.")
        else:
            st.caption("등록된 CJC DB 실사 이미지 라이브러리의 사진으로 드롭다운 교체하거나 이미지를 원고에서 삭제할 수 있습니다.")
            for idx, img_path in enumerate(current_images):
                with st.expander(f"📷 이미지 #{idx+1}: {os.path.basename(img_path)}", expanded=True):
                    img_col_left, img_col_right = st.columns([1, 2])
                    with img_col_left:
                        if os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                        else:
                            st.warning(f"경로 미존재: {img_path}")

                    with img_col_right:
                        # 1. 등록된 DB 이미지 드롭다운 교체
                        current_db_match = next((img for img in all_db_images if img["filepath"] == img_path), None)
                        db_options = ["(현재 이미지 유지)"] + [f"ID:{img['id']} | {img['filename']} - {img['description']}" for img in all_db_images]
                        
                        default_index = 0
                        if current_db_match:
                            target_label = f"ID:{current_db_match['id']} | {current_db_match['filename']} - {current_db_match['description']}"
                            if target_label in db_options:
                                default_index = db_options.index(target_label)

                        selected_db_img = st.selectbox(
                            f"🖼️ DB 라이브러리 사진으로 교체 (#{idx+1})",
                            options=db_options,
                            index=default_index,
                            key=f"{tab_key}_img_select_{idx}"
                        )
                        
                        if selected_db_img != "(현재 이미지 유지)":
                            match_img = next((img for img in all_db_images if f"ID:{img['id']} | {img['filename']} - {img['description']}" == selected_db_img), None)
                            if match_img and os.path.exists(match_img["filepath"]):
                                new_path = match_img["filepath"]
                                if new_path != img_path:
                                    # 미리보기 렌더링용 Base64 치환
                                    new_b64 = llm_router.get_image_src_url({"filepath": new_path})
                                    
                                    article_html = st.session_state["generated_article"]
                                    updated_html = replace_nth_image_in_html(article_html, idx, new_b64)
                                        
                                    st.session_state["generated_article"] = updated_html
                                    current_images[idx] = new_path
                                    st.session_state["generated_image_paths"] = current_images
                                    st.session_state[key_last_article] = ""
                                    st.toast(f"📷 이미지 #{idx+1}이 DB 사진으로 교체되었습니다!", icon="🔄")
                                    st.rerun()

                        # 2. 이미지 삭제 버튼
                        if st.button(f"🗑️ 이미지 #{idx+1} 원고에서 삭제", key=f"{tab_key}_del_img_{idx}"):
                            article_html = st.session_state["generated_article"]
                            updated_html = delete_nth_image_in_html(article_html, idx)
                                
                            st.session_state["generated_article"] = updated_html
                            current_images.pop(idx)
                            st.session_state["generated_image_paths"] = current_images
                            st.session_state.pop(f"{tab_key}_edit_content_input", None)
                            st.toast(f"🗑️ 이미지 #{idx+1}이 원고에서 삭제되었습니다.", icon="✂️")
                            st.rerun()

    # Sub-tab 4: HTML 소스
    with sub_tab4:
        display_code = clean_html_for_editor(st.session_state["generated_article"], st.session_state.get("generated_image_paths", []))
        st.code(display_code, language="html")

    st.divider()

    # 액션 버튼 그룹
    c_copy1, c_copy2, c_send = st.columns([1, 1.2, 1.8])
    with c_copy1:
        if st.button("📌 제목 복사", key=f"copy_title_btn_{tab_key}", use_container_width=True, help="💡 포스팅 메인 제목만 클립보드에 복사합니다."):
            title_text = st.session_state.get("generated_title", "")
            clipboard_manager.copy_html_to_clipboard(title_text)
            st.toast("📌 글 제목이 클립보드에 복사되었습니다!", icon="📋")
    with c_copy2:
        if st.button("📝 본문 복사", key=f"copy_html_btn_{tab_key}", use_container_width=True, help="💡 스마트에디터 서식이 포함된 본문을 클립보드에 복사합니다."):
            clipboard_manager.copy_html_to_clipboard(st.session_state["generated_article"], for_word=True)
            st.toast("📝 본문이 클립보드에 복사되었습니다!", icon="📋")
    with c_send:
        if st.button("🚀 네이버 에디터로 전송 (반자동)", key=f"send_btn_{tab_key}", type="primary", use_container_width=True, help="💡 버튼을 누르면 크롬 브라우저가 열리고 제목, 본문, 실사 사진이 정식 업로드됩니다."):
            if not active_blog_id.strip():
                st.error("⚠️ 네이버 블로그 아이디가 설정되지 않았습니다! 좌측 사이드바에서 본인의 네이버 블로그 아이디를 입력해 주세요.")
            else:
                with st.spinner("네이버 스마트에디터 ONE 구동 및 사진 정식 업로드 중..."):
                    res = naver_publisher.open_naver_smart_editor(
                        title=st.session_state.get("generated_title", "씨제이씨협동조합 포스팅"),
                        html_content=st.session_state["generated_article"],
                        blog_id=active_blog_id.strip(),
                        image_paths=st.session_state.get("generated_image_paths", [])
                    )
                    if res["success"]:
                        st.success(res["message"])
                    else:
                        st.error(res["message"])

    zip_data = create_image_zip(st.session_state.get("generated_image_paths", []))
    if zip_data:
        st.download_button(
            label="🖼️ 원고 실사 사진 팩 1클릭 다운로드 (ZIP)",
            data=zip_data,
            file_name="cjc_article_photos.zip",
            mime="application/zip",
            key=f"dl_zip_btn_{tab_key}",
            use_container_width=True,
            help="💡 네이버 블로그 수동 작성 시 실사 이미지를 ZIP으로 다운로드 받아 올리실 수 있습니다."
        )


# -----------------------------------------------------------------------------
# 4. 메인 탭 구획 (4개 탭)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 최신 뉴스 기사 자동 수집",
    "✍️ 개요 기반 브랜드 포스팅",
    "📊 블로그 & 트렌드 뉴스 대시보드",
    "⚙️ 관리자 설정 (Admin)"
])

# =============================================================================
# TAB 1: 최신 뉴스 기사 자동 수집 및 SEO 최적화 [F-01], [F-02]
# =============================================================================
with tab1:
    st.subheader("📰 최신 뉴스 기사 자동 수집 및 SEO 최적화")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 1. 트렌드 키워드 탐색")
        
        whitelist_kw = config.get("compliance", {}).get("whitelist_seo", ["가발", "탈모", "맞춤가발", "두피케어", "항암가발"])
        options_list = list(dict.fromkeys(whitelist_kw))
        default_kw = [k for k in ["가발", "탈모", "맞춤가발"] if k in options_list]
        
        selected_keywords = st.multiselect(
            "검색할 키워드 선택",
            options=options_list,
            default=default_kw,
            help="💡 네이버 검색에 최적화된 사전 승인 키워드를 기반으로 트렌드 뉴스를 탐색합니다."
        )
        
        limit_count = st.slider("키워드별 가져올 기사 수 (개)", 1, 5, 2, help="선택한 각 키워드마다 검색해 가져올 기사의 개수입니다 (기본 2개).")

        col_filter1, col_filter2, col_filter3, col_filter4, col_filter5 = st.columns([1.5, 1, 1, 1, 1.5])
        with col_filter1:
            enable_relevance_filter = st.checkbox(
                "🎯 기사 관련성 필터링",
                value=True,
                help="💡 가발/탈모 관련 기사만 자동으로 선별하여 수집합니다."
            )
        with col_filter2:
            include_domestic = st.checkbox(
                "🇰🇷 국내 뉴스",
                value=True,
                help="💡 한국어 키워드로 국내 뉴스를 검색합니다 (가발, 탈모, 맞춤가발 등)"
            )
        with col_filter3:
            include_international = st.checkbox(
                "🌍 해외 뉴스",
                value=True,
                help="💡 영어 키워드로 해외 뉴스를 검색합니다 (wig, hair loss, alopecia 등)"
            )
        with col_filter4:
            ignore_dedup = st.checkbox(
                "🧪 중복허용(테스트용)",
                value=False,
                help="💡 체크 시 이미 수집했던 기사도 제외하지 않고 전체 다시 수집합니다."
            )
        with col_filter5:
            enable_semantic_dedup = st.checkbox(
                "🧠 LLM 2차 시맨틱 중복 검증",
                value=False,
                help="💡 체크 시 1차 O(1) 해시 중복 제거 후, AI가 기사 내용의 의미적 유사도(80% 이상 중복)를 2차 필터링합니다."
            )

        # 버튼 영역: 수집 시작 버튼 & 수집 목록 비우기 버튼 상시 노출
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            start_collect = st.button("🔍 최신 뉴스 기사 자동 수집 시작", use_container_width=True, type="primary")
        with btn_col2:
            reset_collect = st.button("🗑️ 수집 목록 비우기", use_container_width=True, help="화면의 기사 목록 및 미리보기를 청소합니다.")

        if start_collect:
            # 선택된 뉴스 소스가 없는 경우 경고
            if not include_domestic and not include_international:
                st.warning("⚠️ 최소 하나 이상의 뉴스 소스를 선택해주세요 (국내 뉴스 또는 해외 뉴스)")
                st.stop()

            # 뉴스 소스에 따른 메시지 표시
            source_message = []
            if include_domestic:
                source_message.append("국내 뉴스")
            if include_international:
                source_message.append("해외 뉴스")

            with st.spinner(f"최신 뉴스 기사 자동 수집 중... ({', '.join(source_message)} 탐색 및 2단계 중복 필터링 적용 중)"):
                res = crawler.fetch_trend_articles(
                    keywords=selected_keywords,
                    limit_per_keyword=limit_count,
                    enable_relevance_filter=enable_relevance_filter,
                    include_domestic=include_domestic,
                    include_international=include_international,
                    ignore_dedup=ignore_dedup,
                    enable_semantic_dedup=enable_semantic_dedup
                )
                if isinstance(res, tuple):
                    articles, stats = res
                else:
                    articles = res
                    stats = {}

                st.session_state["crawled_articles"] = articles
                if articles:
                    if not ignore_dedup:
                        for art in articles:
                            db_manager.save_article_history(art['url'], art['title'], art.get('source', 'RSS'))
                    st.success(f"✨ 뉴스 기사 {len(articles)}건 수집 완료!")
                    if stats:
                        st.info(f"📊 **[수집 & 중복 제거 리포트]** RAW 수집: {stats.get('total_raw', 0)}건 | 🚫 1차 O(1) 해시 중복 제외: {stats.get('dedup_hash_count', 0)}건 | 🧠 2차 LLM 시맨틱 중복 제외: {stats.get('dedup_semantic_count', 0)}건")
                else:
                    st.warning("⚠️ 선택한 키워드의 최신 기사가 모두 이미 수집 완료되었거나 검색 결과가 없습니다. '🧪 중복허용(테스트용)'을 체크하거나 다른 키워드를 선택해 보세요.")

        if reset_collect:
            st.session_state["crawled_articles"] = []
            st.session_state["generated_article"] = ""
            st.session_state["generated_title"] = ""
            st.toast("수집 목록이 비워졌습니다!", icon="🗑️")
            st.rerun()
                    
        st.divider()
        
        # 2. 수집된 기사 목록
        st.markdown("### 2. 수집된 기사 목록")
        if st.session_state["crawled_articles"]:
            filtered_articles = [
                art for art in st.session_state["crawled_articles"]
                if (include_domestic and (art.get("news_type") == "domestic" or art.get("language") == "ko")) or
                   (include_international and (art.get("news_type") == "international" or art.get("language") == "en"))
            ]
            if filtered_articles:
                for idx, art in enumerate(filtered_articles):
                    type_tag = "🇰🇷 국내" if art.get("news_type") == "domestic" or art.get("language") == "ko" else "🌍 해외"
                    with st.expander(f"📌 [{type_tag} | {art['source']}] {art['title'][:30]}...", expanded=(idx==0)):
                        st.write(f"**구분:** {type_tag} 뉴스 | **출처:** {art['source']} ({art.get('published', '')})")
                        summary_label = "**요약 (한글 번역):**" if art.get("summary_original") else "**요약:**"
                        st.write(f"{summary_label} {art['summary']}")
                        if art.get("summary_original"):
                            st.caption(f"🔤 영문 원문: {art['summary_original']}")
                        st.write(f"[원문 기사 링크 보기]({art['url']})")
                        
                        if st.button(f"✨ 이 기사로 SEO 원고 작성", key=f"gen_btn_{idx}"):
                            status_box = st.status("🤖 AI가 기사를 분석하여 PPL 및 SEO 원고를 작성 중입니다...", expanded=True)
                            with status_box:
                                st.write("1️⃣ 외부 기사 메인 메시지 및 맥락 분석 중...")
                                all_db_images = db_manager.get_all_images()
                                seo_res = llm_router.generate_seo_article(
                                    article_title=art['title'],
                                    article_content=art['summary'],
                                    source_url=art['url'],
                                    image_list=all_db_images
                                )
                                
                                if not seo_res.get("success", True):
                                    status_box.update(label="🚨 AI 원고 작성 실패!", state="error", expanded=True)
                                    st.error(f"🚨 **원고 생성 중단:** {seo_res.get('error', 'LLM API 키가 설정되지 않았습니다.')}")
                                    st.info("💡 화면 상단 **[⚙️ 관리자 설정]** 탭으로 이동하여 사용하실 AI 공급사(ChatGPT, Claude, Gemini)의 API Key를 등록한 후 다시 시도해 주세요.")
                                else:
                                    st.write("2️⃣ CJC Fact DB PPL 인용 및 컴플라이언스(의료법) 검증 중...")
                                    db_manager.save_article_history(art['url'], art['title'], art['source'])

                                    st.session_state["generated_article"] = seo_res["content"]
                                    st.session_state["generated_title"] = seo_res["title"]
                                    st.session_state["generated_image_paths"] = seo_res.get("image_paths", [])
                                    
                                    # DB에 원고 생성 이력 즉시 적재
                                    db_manager.save_post_log(
                                        post_type="SEO_ARTICLE",
                                        title=seo_res["title"],
                                        content=seo_res["content"],
                                        status="CREATED",
                                        target_url=art['url']
                                    )
                                    status_box.update(label="✨ SEO 원고 작성 완료! (우측 포스팅 검수 창을 확인하세요)", state="complete", expanded=False)
                                    st.toast("✨ SEO 원고 작성이 완료되었습니다! 우측 창에서 확인하세요.", icon="✅")
                            
                            # JavaScript로 스크롤 이동
                            scroll_js = """
                            <script>
                                setTimeout(function() {
                                    const targetElements = document.querySelectorAll('[data-testid="stVerticalBlock"]');
                                    for (let i = 0; i < targetElements.length; i++) {
                                        if (targetElements[i].textContent.includes('생성된 SEO 포스팅 원고 검수 및 미리보기')) {
                                            targetElements[i].scrollIntoView({ behavior: 'smooth', block: 'start' });
                                            break;
                                        }
                                    }
                                }, 300);
                            </script>
                            """
                            st.markdown(scroll_js, unsafe_allow_html=True)
            else:
                st.info("💡 현재 체크박스 선택(국내/해외)에 해당하는 기사가 없습니다. 체크박스를 변경해보세요.")

    with col2:
        st.markdown("### 3. 생성된 SEO 포스팅 원고 검수 및 미리보기")
        render_article_preview_and_editor("t1", active_blog_id)


# =============================================================================
# TAB 2: 개요 기반 브랜드 포스팅 [F-03]
# =============================================================================
with tab2:
    st.subheader("✍️ 단문 개요(Input) 기반 1,500자 브랜드 포스팅 자동 확장")
    
    st.markdown("""
    <div class="microcopy-box">
        💡 <strong>사용 팁:</strong> 완벽한 문장으로 적지 않으셔도 됩니다. 
        <em>'가발 창업반 4기 모집', '선착순 10명', '다음 주 화요일 마감'</em>처럼 전달하고 싶은 핵심 단어만 2~3줄로 입력하시면 AI가 씨제이씨협동조합의 브랜드 톤앤매너를 입혀 1,500자의 정식 글로 완성합니다.
    </div>
    """, unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns([1, 1])
    
    with b_col1:
        post_category = st.selectbox(
            "포스팅 유형 선택",
            options=[
                "B2C 잠재고객 맞춤가발/항암가발 안내",
                "B2B 가발창업 및 두피전문교육 수강생 모집",
                "매장 공지사항 및 휴무일 안내",
                "신제품 출시 및 프로모션 홍보"
            ],
            help="💡 안내할 글의 성격에 맞춰 AI가 고객 맞춤 어조로 문맥을 조정합니다."
        )
        
        post_outline = st.text_area(
            "전달할 핵심 개요 (단문 입력)",
            height=160,
            placeholder="예시:\n- 추석 명절 휴무 안내 9월 15일~18일\n- ATUM 3D 무료 측정 이벤트 실시\n- 선착순 20명 영양 오일 증정",
            help="💡 전달하고자 하는 주요 내용 및 일정을 간단한 메모 형태로 작성해주세요."
        )
        
        if st.button("🪄 1,500자 브랜드 포스팅 완성하기", type="primary", use_container_width=True):
            if not post_outline.strip():
                st.warning("핵심 개요 내용을 입력해주세요!")
            else:
                status_b = st.status("🤖 AI 브랜드 콘텐츠 디렉터가 글을 확장 및 완성하고 있습니다...", expanded=True)
                with status_b:
                    st.write("1️⃣ 입력 개요 분석 및 톤앤매너 설정 중...")
                    all_db_images = db_manager.get_all_images()
                    brand_res = llm_router.generate_brand_expansion_article(
                        post_category=post_category,
                        post_outline=post_outline,
                        image_list=all_db_images
                    )
                    
                    if not brand_res.get("success", True):
                        status_b.update(label="🚨 AI 브랜드 원고 작성 실패!", state="error", expanded=True)
                        st.error(f"🚨 **원고 생성 중단:** {brand_res.get('error', 'LLM API 키가 설정되지 않았습니다.')}")
                        st.info("💡 화면 상단 **[⚙️ 관리자 설정]** 탭으로 이동하여 사용하실 AI 공급사(ChatGPT, Claude, Gemini)의 API Key를 등록한 후 다시 시도해 주세요.")
                    else:
                        st.write("2️⃣ 1,500자 원고 구성 및 서식 정제 중...")
                        st.session_state["generated_article"] = brand_res["content"]
                        st.session_state["generated_title"] = brand_res["title"]
                        st.session_state["generated_image_paths"] = brand_res.get("image_paths", [])
                        
                        # DB에 브랜드 원고 생성 이력 즉시 적재
                        db_manager.save_post_log(
                            post_type="BRAND_ARTICLE",
                            title=brand_res["title"],
                            content=brand_res["content"],
                            status="CREATED"
                        )
                        status_b.update(label="✨ 브랜드 포스팅 작성 완료! (우측 포스팅 검수 창을 확인하세요)", state="complete", expanded=False)
                        st.toast("✨ 브랜드 원고 작성이 완료되었습니다!", icon="✅")

    with b_col2:
        st.markdown("### 📄 완성된 브랜드 포스팅 미리보기")
        render_article_preview_and_editor("t2", active_blog_id)


# =============================================================================
# TAB 3: 네이버 블로그 자동 발행 & 모니터링
# =============================================================================
with tab3:
    t3_head1, t3_head2 = st.columns([3.5, 1])
    with t3_head1:
        st.subheader("📊 블로그 & 트렌드 뉴스 종합 대시보드")
        st.caption("AI 블로그 원고 생성 실적, 수집 뉴스 트렌드, 네이버 전송 결과 및 이미지 자산을 한눈에 모니터링합니다.")
    with t3_head2:
        if st.button("🔄 실시간 새로고침", key="ref_dash_btn", use_container_width=True, help="💡 최신 DB 적재 데이터 및 메트릭을 실시간으로 다시 로드합니다."):
            st.rerun()
    
    # DB 통계 데이터 로드
    stats = db_manager.get_dashboard_stats()
    
    # 1. 상단 KPI 메트릭 카드 (4종)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("📌 총 원고 생성 수", f"{stats['total_posts']}건", delta="AI 자동 작성")
    with kpi2:
        st.metric("🚀 네이버 전송 완료", f"{stats['naver_published']}건", delta="스마트에디터 연동")
    with kpi3:
        st.metric("📰 아카이빙 뉴스 수", f"{stats['archived_articles']}건", delta="O(1) 중복 제거")
    with kpi4:
        st.metric("📷 실사 이미지 자산", f"{stats['total_images']}개", delta="라이브러리 보유")
        
    st.divider()
    
    # 2. 시각화 통계 차트 (2열 구획)
    chart_col1, chart_col2 = st.columns([1.2, 1])
    
    # 전체 로그 데이터프레임 로드
    raw_logs = db_manager.get_all_post_logs()
    df_posts = pd.DataFrame(raw_logs) if raw_logs else pd.DataFrame(columns=["id", "post_type", "title", "content", "status", "target_url", "created_at"])
    
    with chart_col1:
        st.markdown("#### 📈 일자별 포스팅 생성 및 전송 현황")
        if not df_posts.empty and "created_at" in df_posts.columns:
            try:
                df_posts["date"] = pd.to_datetime(df_posts["created_at"]).dt.date
                daily_counts = df_posts.groupby(["date", "post_type"]).size().unstack(fill_value=0)
                st.bar_chart(daily_counts, use_container_width=True)
            except Exception as e:
                st.info("💡 데이터 집계 중... 원고를 작성하시면 일자별 생성 추이가 시각화됩니다.")
        else:
            st.info("💡 아직 생성된 포스팅 기록이 없습니다. 원고를 작성하시면 일자별 생성 추이가 시각화됩니다.")
            
    with chart_col2:
        st.markdown("#### 📊 포스팅 유형 및 전송 상태 비율")
        if not df_posts.empty and "post_type" in df_posts.columns:
            type_counts = df_posts["post_type"].value_counts()
            st.bar_chart(type_counts, use_container_width=True)
        else:
            st.info("💡 데이터가 쌓이면 SEO 글 vs 브랜드 포스팅 비율이 시각화됩니다.")

    st.divider()

    # 3. 실시간 포스팅 이력 상세 데이터 테이블 & 검색/필터링
    st.markdown("#### 📋 포스팅 생성 및 전송 이력 상세 로그")
    
    d_col1, d_col2 = st.columns([2, 1])
    with d_col1:
        search_query = st.text_input("🔍 글 제목 검색", placeholder="검색할 글 제목 입력...", help="글 제목으로 이력을 필터링합니다.")
    with d_col2:
        status_filter = st.selectbox("전송 상태 필터", options=["전체", "WAITING_FOR_USER_PUBLISH", "SUCCESS", "ERROR"])
        
    filtered_df = df_posts.copy()
    if not filtered_df.empty:
        if search_query.strip():
            filtered_df = filtered_df[filtered_df["title"].str.contains(search_query.strip(), case=False, na=False)]
        if status_filter != "전체":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]
            
        st.dataframe(
            filtered_df[["id", "created_at", "post_type", "title", "status", "target_url"]],
            column_config={
                "id": "ID",
                "created_at": "생성 일시",
                "post_type": "포스팅 유형",
                "title": "글 제목",
                "status": "전송 상태",
                "target_url": "네이버 블로그 URL"
            },
            use_container_width=True,
            height=280
        )
    else:
        st.write("표시할 포스팅 로그가 없습니다.")

    st.divider()

    # 4. 포스팅 데이터 및 이력 관리 (1클릭 리셋 및 CSV 다운로드)
    st.markdown("#### ⚙️ 포스팅 데이터 및 이력 관리")
    m_action1, m_action2 = st.columns([1, 1])
    
    with m_action1:
        if not df_posts.empty:
            csv_bytes = df_posts.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

            # 브라우저 다운로드 버튼
            st.download_button(
                label="📥 브라우저 다운로드",
                data=csv_bytes,
                file_name="cjc_blog_posting_history.csv",
                mime="text/csv",
                key="download_post_history_csv",
                use_container_width=True,
                help="💡 브라우저 다운로드 폴더로 저장됩니다. 안되면 아래 직접 저장을 사용하세요."
            )

            # 직접 저장 버튼 (다운로드 폴더를 찾을 수 없는 경우)
            if st.button("💻 바탕화면/문서에 직접 저장", use_container_width=True, key="save_directly"):
                import datetime
                import os

                # 바탕화면과 문서 디렉토리 확인
                save_locations = []
                desktop_path = os.path.expanduser("~/Desktop")
                documents_path = os.path.expanduser("~/Documents")

                if os.path.exists(desktop_path):
                    save_locations.append(desktop_path)
                if os.path.exists(documents_path):
                    save_locations.append(documents_path)
                if save_locations:
                    save_path = save_locations[0]  # 첫 번째 가능한 위치 사용
                else:
                    save_path = os.getcwd()  # 현재 작업 디렉토리

                # 파일명에 타임스탬프 추가
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cjc_blog_history_{timestamp}.csv"
                full_path = os.path.join(save_path, filename)

                try:
                    with open(full_path, 'wb') as f:
                        f.write(csv_bytes)

                    st.success(f"✅ CSV 파일이 저장되었습니다!")
                    st.info(f"📍 저장 위치: `{full_path}`")
                    st.info("💡 Finder에서 파일을 더블클릭하면 엑셀로 열립니다.")
                except Exception as e:
                    st.error(f"❌ 저장 실패: {e}")

        else:
            st.button("📥 포스팅 전체 이력 엑셀/CSV 다운로드", disabled=True, use_container_width=True)

    with m_action2:
        if st.button("🧹 포스팅 로그 및 DB 기록 초기화 (테스트용)", type="secondary", use_container_width=True, help="💡 지금까지 쌓인 포스팅 생성 로그 및 크롤링 이력 기록을 1클릭으로 초기화합니다."):
            db_manager.clear_all_logs()
            st.success("🧹 포스팅 이력 및 아카이빙 DB 데이터가 모두 초기화되었습니다!")
            st.rerun()


# =============================================================================
# TAB 4: 시스템 및 AI 모델 설정 (Admin Settings)
# =============================================================================
with tab4:
    st.subheader("⚙️ 시스템 및 AI 모델 설정 (Admin Settings)")
    st.caption("AI 공급사별 모델명, API 키, 브랜드 페르소나, 핵심 기술 DB, SEO 키워드 및 의료법 치환 규칙을 통합 관리합니다.")
    
    # 저장 결과 메시지 알림 처리
    if "admin_save_msg" in st.session_state:
        msg_data = st.session_state.pop("admin_save_msg")
        if msg_data["type"] == "success":
            st.success(msg_data["text"])
            st.info(msg_data["details"])
            st.toast("✅ 설정 저장 완료!", icon="💾")
        else:
            st.error(msg_data["text"])
            st.toast("❌ 설정 저장 실패!", icon="🚨")
            
    # 1. AI 공급사 및 API Key 관리 (ChatGPT, Claude, Gemini 구분 및 테스트)
    st.markdown("#### 1. AI 모델 및 API 키 관리 (AI Provider & API Key Settings)")
    st.caption("💡 ChatGPT, Claude, Gemini 중 사용할 메인 AI 엔진을 선택하고, 모델명과 API 키를 직접 입력 및 검증할 수 있습니다.")
    
    llm_cfg = config.get("llm_settings", {})
    provider_options = ["ChatGPT", "Claude", "Gemini"]
    curr_provider = llm_cfg.get("active_provider", "Gemini")
    prov_index = provider_options.index(curr_provider) if curr_provider in provider_options else 2
    
    active_provider = st.radio(
        "🎯 포스팅 생성에 사용할 메인 AI 엔진 선택 (Primary AI Engine):",
        options=provider_options,
        index=prov_index,
        horizontal=True,
        help="선택한 AI 엔진의 모델과 API 키가 원고 생성 시 적용됩니다."
    )
    
    models_cfg = llm_cfg.get("models", {})
    api_keys_cfg = llm_cfg.get("api_keys", {})
    
    col_gpt, col_claude, col_gemini = st.columns(3)
    
    with col_gpt:
        st.markdown("##### 🟢 OpenAI (ChatGPT)")
        gpt_model_input = st.text_input(
            "ChatGPT 모델명 (Model)",
            value=models_cfg.get("chatgpt", "gpt-4o"),
            key="input_chatgpt_model",
            help="예: gpt-4o, gpt-4o-mini, gpt-4-turbo 등"
        )
        gpt_key_input = st.text_input(
            "OpenAI API Key",
            value=api_keys_cfg.get("openai", ""),
            type="password",
            key="input_chatgpt_key"
        )
        if st.button("🧪 ChatGPT 연결 테스트", key="btn_test_chatgpt", use_container_width=True):
            with st.spinner("ChatGPT API 연결 테스트 중..."):
                test_res = llm_router.test_llm_connection("chatgpt", gpt_model_input, gpt_key_input)
                if test_res["success"]:
                    st.success(test_res["message"])
                else:
                    st.error(test_res["message"])

    with col_claude:
        st.markdown('##### 🟣 <span translate="no" class="notranslate">Anthropic</span> (Claude)', unsafe_allow_html=True)
        claude_model_input = st.text_input(
            "Claude 모델명 (Model)",
            value=models_cfg.get("claude", "claude-3-5-sonnet-20241022"),
            key="input_claude_model",
            help="예: claude-3-5-sonnet-20241022, claude-3-haiku-20240307 등"
        )
        claude_key_input = st.text_input(
            "Anthropic API Key",
            value=api_keys_cfg.get("anthropic", ""),
            type="password",
            key="input_claude_key"
        )
        if st.button("🧪 Claude 연결 테스트", key="btn_test_claude", use_container_width=True):
            with st.spinner("Claude API 연결 테스트 중..."):
                test_res = llm_router.test_llm_connection("claude", claude_model_input, claude_key_input)
                if test_res["success"]:
                    st.success(test_res["message"])
                else:
                    st.error(test_res["message"])

    with col_gemini:
        st.markdown("##### 🔵 Google (Gemini)")
        gemini_model_input = st.text_input(
            "Gemini 모델명 (Model)",
            value=models_cfg.get("gemini", "gemini-2.5-flash"),
            key="input_gemini_model",
            help="예: gemini-2.5-flash, gemini-1.5-flash, gemini-1.5-pro 등"
        )
        gemini_key_input = st.text_input(
            "Google API Key",
            value=api_keys_cfg.get("google", ""),
            type="password",
            key="input_gemini_key"
        )
        if st.button("🧪 Gemini 연결 테스트", key="btn_test_gemini", use_container_width=True):
            with st.spinner("Gemini API 연결 테스트 중..."):
                test_res = llm_router.test_llm_connection("gemini", gemini_model_input, gemini_key_input)
                if test_res["success"]:
                    st.success(test_res["message"])
                else:
                    st.error(test_res["message"])

    st.divider()

    with st.form("admin_config_form"):
        # 2. 페르소나 및 Few-Shot
        st.markdown("#### 2. 브랜드 페르소나 및 작성 톤앤매너 설정 (Brand Persona & Tone of Voice)")
        persona_guide = config.get("persona_guide", {})
        persona_desc = st.text_area("시스템 페르소나 정의 (System Persona)", value=persona_guide.get("system_persona", ""), height=70)
        
        st.divider()
        
        # 3. 조합 팩트 DB (RAG)
        st.markdown("#### 3. 씨제이씨협동조합 핵심 기술 DB (Company Knowledge Base)")
        fact_db = config.get("fact_database", {}).get("company_facts", [])
        facts_text = st.text_area(
            "조합 핵심 기술 및 브랜드 팩트 (줄바꿈으로 구획)",
            value="\n".join(fact_db),
            height=120,
            help="💡 포스팅 원고 작성 시 AI가 본 패널의 팩트를 필수 인용합니다."
        )
        
        st.divider()
        
        # 4. SEO 키워드 및 의료법 금기어
        st.markdown("#### 4. SEO 키워드 & 의료법 준수 치환 사전 (SEO & Compliance Rules)")
        st.markdown("""
        <div class="microcopy-box" style="margin-bottom: 15px;">
            🛡️ <strong>의료법 및 표시광고법 컴플라이언스 가이드:</strong><br>
            가발 및 두피케어 브랜드는 의료기관이나 의약품이 아니므로 '치료', '완치', '재생' 등의 표현 사용 시 게시물 중단 및 법적 리스크가 발생합니다.<br>
            아래 사전 표에 금기어와 안전한 치환어를 등록하시면, AI 원고 작성 및 원고 재검토(Audit) 시 <strong>자동으로 100% 실시간 감지 및 교정</strong>됩니다. (행 추가/삭제 가능)
        </div>
        """, unsafe_allow_html=True)
        
        compliance_cfg = config.get("compliance", {})
        whitelist_input = st.text_input(
            "SEO 화이트리스트 추천 키워드 (쉼표로 구분)",
            value=", ".join(compliance_cfg.get("whitelist_seo", []))
        )
        
        st.markdown("##### 🚫 의료법 및 표시광고법 금기어 치환 사전 (Blacklist Compliance Dictionary)")
        st.caption("💡 표 하단의 [+] 행 추가 버튼을 눌러 새로운 금기어와 안전한 치환어를 등록할 수 있습니다.")
        
        blacklist_map = compliance_cfg.get("blacklist_map", {})
        df_blacklist = pd.DataFrame([
            {"금기어 (Prohibited)": k, "치환어 (Replacement)": v}
            for k, v in blacklist_map.items()
        ])
        
        edited_df = st.data_editor(
            df_blacklist,
            num_rows="dynamic",
            use_container_width=True
        )
        
        st.divider()
        
        submitted = st.form_submit_button("💾 전체 설정 동기화 저장", type="primary", use_container_width=True)
        
        if submitted:
            try:
                import datetime
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 선택된 공급사의 모델명 결정
                if active_provider == "ChatGPT":
                    act_model = gpt_model_input.strip() or "gpt-4o"
                elif active_provider == "Claude":
                    act_model = claude_model_input.strip() or "claude-3-5-sonnet-20241022"
                else:
                    act_model = gemini_model_input.strip() or "gemini-2.5-flash"
                
                # 변경된 데이터 수집 및 config.json 저장
                new_config = {
                    "llm_settings": {
                        "active_provider": active_provider,
                        "active_model": act_model,
                        "models": {
                            "chatgpt": gpt_model_input.strip(),
                            "claude": claude_model_input.strip(),
                            "gemini": gemini_model_input.strip()
                        },
                        "api_keys": {
                            "openai": gpt_key_input.strip(),
                            "anthropic": claude_key_input.strip(),
                            "google": gemini_key_input.strip()
                        }
                    },
                    "persona_guide": {
                        "system_persona": persona_desc,
                        "few_shot_samples": persona_guide.get("few_shot_samples", [])
                    },
                    "fact_database": {
                        "company_facts": [f.strip() for f in facts_text.split("\n") if f.strip()]
                    },
                    "compliance": {
                        "whitelist_seo": [k.strip() for k in whitelist_input.split(",") if k.strip()],
                        "blacklist_map": {
                            row["금기어 (Prohibited)"]: row["치환어 (Replacement)"]
                            for _, row in edited_df.iterrows()
                            if row["금기어 (Prohibited)"]
                        }
                    },
                    "google_sheets": config.get("google_sheets", {})
                }
                save_config_data(new_config)
                
                fact_count = len(new_config['fact_database']['company_facts'])
                blacklist_count = len(new_config['compliance']['blacklist_map'])
                
                st.session_state["admin_save_msg"] = {
                    "type": "success",
                    "text": f"✅ 관리자 설정이 config.json 파일에 정상적으로 동기화 저장되었습니다! (저장 시각: {now_str})",
                    "details": f"📌 **저장 내역 요약:**\n- **메인 AI 엔진:** `{active_provider}` (모델명: `{act_model}`)\n- **조합 기술 DB:** 총 {fact_count}개 팩트 항목 반영\n- **의료법 준수 사전:** 총 {blacklist_count}개 치환 규칙 반영"
                }
            except Exception as e:
                st.session_state["admin_save_msg"] = {
                    "type": "error",
                    "text": f"❌ 설정 저장 중 오류가 발생했습니다: {str(e)}"
                }
            st.rerun()

    st.divider()

    # 5. 실사 이미지 라이브러리 관리 (AI 원고 문맥 자동 매칭)
    st.markdown("#### 5. 📷 실사 이미지 라이브러리 관리 (AI 원고 문맥 자동 매칭)")
    st.markdown("""
    <div class="microcopy-box">
        💡 <strong>이미지 관리 가이드:</strong> 조합의 ATUM 3D 두상스캐너 측정 모습, 키노피스 가발 제품, 매장/임상, 창업교육 현장 등의 실사 사진을 업로드하고 설명을 입력해주세요.<br>
        AI가 블로그 포스팅을 작성할 때 본문 소제목 문맥과 가장 일치하는 이미지를 <strong>3~5장 자동 선별하여 원고 중간에 배치</strong>해 드립니다.
    </div>
    """, unsafe_allow_html=True)

    img_col1, img_col2 = st.columns([1, 1])

    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_images")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with img_col1:
        st.markdown("##### 📥 신규 실사 이미지 등록")
        
        uploaded_file = st.file_uploader(
            "📷 컴퓨터 이미지 파일 선택 (Browse files)",
            type=["png", "jpg", "jpeg", "webp"],
            key="cjc_file_uploader_direct",
            help="💡 [Browse files] 버튼을 눌러 컴퓨터 내 이미지 파일(PNG, JPG, WEBP 등)을 선택하세요."
        )
        if uploaded_file:
            st.image(uploaded_file, caption=f"선택된 파일: {uploaded_file.name}", use_container_width=True)

        img_desc_input = st.text_input(
            "이미지 상세 설명 (AI 문맥 매칭용 필수)",
            placeholder="예: ATUM 3D 두상스캐너로 10분 만에 두상을 측정하는 모습",
            key="img_desc_input_key_direct",
            help="💡 AI가 본 설명 문구를 읽고 블로그 포스팅 소제목 및 문맥에 맞춰 최적의 이미지를 자동 선정합니다."
        )

        img_cat_input = st.selectbox(
            "카테고리 구분",
            options=["제품/기술", "매장/임상", "창업/교육", "기타"],
            key="img_cat_input_key_direct"
        )

        if st.button("📥 이미지 등록하기", type="primary", use_container_width=True, key="btn_save_cjc_image"):
            if not uploaded_file:
                st.warning("⚠️ 상단의 [Browse files] 버튼을 눌러 등록할 이미지 파일을 먼저 선택해 주세요!")
            elif not img_desc_input.strip():
                st.warning("⚠️ AI가 문맥을 인식할 수 있도록 이미지 상세 설명을 입력해 주세요!")
            else:
                try:
                    import uuid
                    ext = os.path.splitext(uploaded_file.name)[1].lower()
                    if not ext:
                        ext = ".png"
                    unique_filename = f"{uuid.uuid4().hex[:10]}{ext}"
                    save_path = os.path.join(UPLOAD_DIR, unique_filename)

                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    db_manager.save_image_metadata(
                        filename=uploaded_file.name,
                        filepath=save_path,
                        description=img_desc_input.strip(),
                        category=img_cat_input
                    )
                    st.toast("📷 새로운 실사 이미지가 라이브러리에 등록되었습니다!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 이미지 저장 오류: {e}")

    with img_col2:
        st.markdown("##### 🖼️ 등록된 이미지 라이브러리 목록")
        current_images = db_manager.get_all_images()

        if current_images:
            st.caption(f"총 {len(current_images)}개의 실사 이미지가 등록되어 있습니다.")
            for img in current_images:
                with st.expander(f"📌 [{img['category']}] {img['description'][:25]}...", expanded=False):
                    if os.path.exists(img['filepath']):
                        st.image(img['filepath'], caption=img['description'], use_container_width=True)
                    st.write(f"**파일명:** `{img['filename']}`")
                    st.write(f"**카테고리:** {img['category']}")
                    st.write(f"**설명:** {img['description']}")
                    st.write(f"**등록일:** {img['created_at']}")

                    # 이미지 수정 폼
                    with st.form(key=f"edit_img_form_{img['id']}"):
                        st.markdown("##### 📝 이미지 정보 수정")
                        edit_desc = st.text_input(
                            "설명 수정",
                            value=img['description'],
                            key=f"edit_desc_{img['id']}",
                            help="이미지 상세 설명 (AI 문맥 매칭용)"
                        )
                        edit_category = st.selectbox(
                            "카테고리 수정",
                            options=["제품/기술", "매장/임상", "창업/교육", "기타"],
                            index=["제품/기술", "매장/임상", "창업/교육", "기타"].index(img['category']) if img['category'] in ["제품/기술", "매장/임상", "창업/교육", "기타"] else 0,
                            key=f"edit_cat_{img['id']}"
                        )

                        col_edit1, col_edit2 = st.columns(2)
                        with col_edit1:
                            if st.form_submit_button("💾 수정 저장", type="primary", use_container_width=True):
                                if db_manager.update_image_metadata(
                                    img['id'],
                                    description=edit_desc.strip(),
                                    category=edit_category
                                ):
                                    st.toast("✅ 이미지 정보가 수정되었습니다!", icon="💾")
                                    st.rerun()
                                else:
                                    st.error("❌ 수정에 실패했습니다.")

                        with col_edit2:
                            if st.form_submit_button("🗑️ 이미지 삭제", use_container_width=True):
                                if db_manager.delete_image(img['id']):
                                    st.toast("이미지가 삭제되었습니다!", icon="🗑️")
                                    st.rerun()
        else:
            st.info("💡 등록된 실사 이미지가 없습니다. 좌측에서 사진을 등록하면 AI가 원고 생성 시 자동으로 이미지 3~5장을 삽입해 드립니다.")
