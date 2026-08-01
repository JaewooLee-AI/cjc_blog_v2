import json
import os
import re
from typing import Dict, Any, Optional, List, Tuple

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> Dict[str, Any]:
    """config.json 및 .env 환경변수 동시 실시간 로드 (보안 유지를 위한 .env 자동 연동)"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            api_keys = cfg.setdefault("llm_settings", {}).setdefault("api_keys", {})
            if not api_keys.get("google"):
                api_keys["google"] = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
            if not api_keys.get("openai"):
                api_keys["openai"] = os.getenv("OPENAI_API_KEY", "")
            if not api_keys.get("anthropic"):
                api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY", "")
            return cfg
    return {}

def format_html_for_naver_editor(html_text: str) -> str:
    """
    네이버 스마트에디터 ONE 서식 호환성을 위한 HTML 포맷터.
    - 본문 맨 첫 줄의 <h1> (또는 메인 제목 파라그래프)를 제거하여 네이버 본문에 제목이 중복 작성되는 현상 방지
    - <h2>, <h3>, <p> 태그를 네이버 스마트에디터 최적화 인라인 CSS 스타일로 변환
    """
    text = html_text.strip()
    
    # 마크다운 코드블록 (```html ... ```) 제거
    text = re.sub(r"^```html\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    
    # 본문 내 메인 제목 태그(<h1>...</h1>) 완전 제거 (메인 제목은 상단 제목 입력 칸으로만 전송됨)
    text = re.sub(r"<h1[^>]*>.*?</h1>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<p style=\"[^\"]*font-size:\s*2[0-9]px[^\"]*\">.*?</p>(?:<br\s*/?>)?", "", text, flags=re.IGNORECASE | re.DOTALL)
    
    # 취소선(~~, <del>, <s>, <strike>) 서식 완전 제거 (네이버 에디터 취소선 변환 오작동 방지)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"<(?:del|s|strike)[^>]*>(.*?)</(?:del|s|strike)>", r"\1", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"text-decoration:\s*line-through;?", "", text, flags=re.IGNORECASE)

    # <h2> 태그 변환 (소제목 서식)
    text = re.sub(
        r"<h2[^>]*>(.*?)</h2>",
        r'<br><p style="font-size: 18px; font-weight: bold; color: #312E81; margin-top: 20px; margin-bottom: 10px; line-height: 1.5;">\1</p><br>',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # <h3> 태그 변환 (세부소제목 서식)
    text = re.sub(
        r"<h3[^>]*>(.*?)</h3>",
        r'<br><p style="font-size: 16px; font-weight: bold; color: #4338CA; margin-top: 14px; margin-bottom: 6px; line-height: 1.5;">\1</p><br>',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    return text

def sanitize_compliance(text: str, config: Optional[Dict[str, Any]] = None) -> str:
    """의료법 및 과대광고 방지 정규표현식/문자열 치환 파이프라인 (Sanitization)"""
    if config is None:
        config = load_config()
        
    formatted = format_html_for_naver_editor(text)
    
    blacklist_map = config.get("compliance", {}).get("blacklist_map", {})
    sanitized_text = formatted
    
    for forbidden, replacement in blacklist_map.items():
        if forbidden in sanitized_text:
            pattern = re.compile(re.escape(forbidden), re.IGNORECASE)
            sanitized_text = pattern.sub(replacement, sanitized_text)
            
    return sanitized_text

# [템플릿 A] 해외/국내 트렌드 정보성 SEO 글 작성용
PROMPT_TEMPLATE_A = """
너는 {system_persona} 역할을 완벽하게 수행하는 수석 뷰티 에디터이자 마케팅 전문가다.
아래에 제공된 외부 해외/국내 트렌드 뉴스의 핵심 정보를 파악하여, 네이버 블로그 검색 노출(SEO)에 최적화된 1,500자 이상의 양질의 정보성 포스팅 원고를 작성하라.

[문체 및 고품질 한국어 작성 지침 (필수)]
1. 100% 자연스럽고 품격 있는 한국어 문어체/구어체(네이버 블로그 스타일)로 작성하라.
2. 영어 직역투나 어색한 번역기 문체(예: '체중 감량을 하는 사람들', '자연과 복부 가발', '통일된 생각' 등)를 절대로 사용하지 마라. 외신 뉴스나 전문 보고서 내용이 있더라도 대한민국 독자가 읽기 쉬운 매끄럽고 세련된 한국어 문장으로 완벽히 각색하라.
3. 글의 맨 첫 줄에는 <h1>블로그 포스팅 메인 제목</h1> 양식으로 매력적인 제목 1개만 작성하라. (이 제목은 에디터의 제목 칸으로 자동 추출됩니다.)

[핵심 반영 및 구조화 지침]
1. 서론 (공감 형성): 입력된 기사의 트렌드나 문제의식(예: 탈모 인구의 급증, 기존 가발의 화학물질 부작용 등)을 독자에게 친절하게 설명하며 고민에 깊이 공감하라.
2. 본론 (해결책 전환 및 브랜드 PPL): 외부 기사의 정보와 자연스러운 논리로 연결하여, 씨제이씨협동조합의 독보적인 기술 인프라가 완벽한 대안임을 강조하라. 
   - 반드시 아래 제공된 우리 조합의 핵심 팩트(Fact DB) 중 2개 이상을 문맥에 맞게 인용할 것.
   - [조합 핵심 팩트 DB]:
{fact_database}
3. SEO 타깃 키워드 배치: 글 전체(제목 포함)에 걸쳐 다음의 화이트리스트 키워드를 가장 자연스러운 형태로 3~5회 분산 배치하라.
   - [필수 키워드 목록]: {whitelist_keywords}
4. 출처 표기 자동화: 저작권과 공신력을 위해, 글의 마지막 단락에는 반드시 [원문 기사 출처: {source_url}] 양식을 덧붙여라.
5. 금기어 정책 (법적 리스크 방지): 절대 의학적 치료 효과를 보장하거나 오인하게 만드는 단어({blacklist_keys})를 사용하지 마라. 발견 즉시 보완, 케어 등의 단어로 우회하라.

{image_instructions}

[입력된 외부 기사 데이터]
- 기사 제목: {article_title}
- 기사 본문 요약: {article_content}

[출력 형식 제한]
네이버 스마트에디터에 붙여넣었을 때 시각적으로 완성도를 띠도록 HTML 태그(<h1>, <h2>, <p>, <strong>, <br> 등)를 적극적으로 활용하여 포맷팅하라.
제목은 <h1> 태그로 시작하고, 소제목은 <h2>, 본문 단락은 <p> 태그로 구성하라.
"""

# [템플릿 B] 실무자 개요 입력 기반 브랜드 공지/마케팅 글 작성용
PROMPT_TEMPLATE_B = """
너는 {system_persona} 역할을 수행하는 씨제이씨협동조합의 수석 브랜드 콘텐츠 디렉터다.
아래 실무자가 입력한 거칠고 짧은 단어 중심의 개요(Outline)를 바탕으로, 타깃 고객과 소상공인분들의 마음을 사로잡는 따뜻하고 논리적인 1,500자 내외의 브랜드 공식 포스팅을 완성하라.

[문체 및 고품질 한국어 작성 지침 (필수)]
1. 100% 자연스럽고 매끄러운 고급 한국어 블로그 어조로 작성하라. 번역투 문장이나 어색한 표현을 절대 배제하라.
2. 글의 맨 첫 줄에는 <h1>블로그 포스팅 메인 제목</h1> 양식으로 브랜드 공지 제목 1개만 작성하라.

[작성 및 톤앤매너 극대화 지침]
1. 완벽한 톤앤매너 모방 (Few-Shot): 아래에 제공된 우리 조합의 과거 우수 포스팅 샘플을 심도 있게 분석하여, 그 특유의 어조, 높임말의 형태, 단락을 나누는 호흡을 100% 동일하게 모방하라.
   - [우수 포스팅 참조 샘플]:
{few_shot_samples}
2. 도입부 비전 세팅: 60년 동안 정체되어 온 가발 산업을 혁신하는 '대한가발협회 소속 씨제이씨협동조합'의 철학(상생, 디지털 대전환, ESG 경영)을 가볍게 터치하며 신뢰감을 주면서 글을 시작하라.
3. 본문 확장 (Expansion): 실무자가 입력한 핵심 내용이 단 하나도 누락되어서는 안 되며, 무미건조한 단어들에 살을 붙여 고객이 이해하기 쉽도록 구체적이고 친절하게 풀어서 설명하라. 
4. 결론 및 CTA (Call to Action): 독자가 글을 다 읽은 후 자연스럽게 가까운 조합 가맹점 방문을 예약하거나, 창업 교육 문의, 혹은 ATUM 3D 두상측정기 도입을 고려하도록 유도하는 부드러운 맺음말을 작성하라.

{image_instructions}

[실무자 입력 데이터]
- 포스팅 유형: {post_category}
- 주요 전달 개요: {post_outline}

[출력 형식 제한]
네이버 에디터에 그대로 붙여넣을 수 있도록, 글의 제목은 <h1> 태그로 감싸고, 소제목은 <h2>, 본문 내 강조할 부분은 <strong> 태그를 사용하여 시각적으로 아름답게 구조화된 HTML 문서를 반환하라.
"""

def test_llm_connection(provider: str, model_name: str, api_key: str) -> Dict[str, Any]:
    """[ChatGPT / Claude / Gemini] LLM 모델명 및 API Key 연결 정상 작동 여부 실시간 테스트"""
    prov = provider.strip().lower()
    clean_key = api_key.strip()
    clean_model = model_name.strip()
    
    if not clean_key:
        return {
            "success": False,
            "message": f"⚠️ [{provider}] API Key가 입력되지 않았습니다."
        }
        
    test_prompt = "안녕하세요! 연결 테스트입니다. 'OK'라고만 짧게 답변해 주세요."
    
    # 1. ChatGPT (OpenAI)
    if "chatgpt" in prov or "openai" in prov or "gpt" in prov:
        m_name = clean_model if clean_model else "gpt-4o"
        try:
            from openai import OpenAI
            client = OpenAI(api_key=clean_key)
            response = client.chat.completions.create(
                model=m_name,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=15,
                temperature=0.1
            )
            reply = response.choices[0].message.content.strip()
            return {
                "success": True,
                "message": f"🟢 ChatGPT 연결 성공! 모델: '{m_name}' | 응답: '{reply}'"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ ChatGPT 연결 실패 (모델: '{m_name}'): {e}"
            }
            
    # 2. Claude (Anthropic)
    elif "claude" in prov or "anthropic" in prov:
        m_name = clean_model if clean_model else "claude-3-5-sonnet-20241022"
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=clean_key)
            response = client.messages.create(
                model=m_name,
                max_tokens=15,
                messages=[{"role": "user", "content": test_prompt}]
            )
            reply = response.content[0].text.strip()
            return {
                "success": True,
                "message": f"🟣 Claude 연결 성공! 모델: '{m_name}' | 응답: '{reply}'"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Claude 연결 실패 (모델: '{m_name}'): {e}"
            }
            
    # 3. Gemini (Google GenAI)
    elif "gemini" in prov or "google" in prov:
        m_name = clean_model if clean_model else "gemini-2.5-flash"
        if "gemini-2.0" in m_name:
            m_name = "gemini-2.5-flash"
            
        try:
            from google import genai
            client = genai.Client(api_key=clean_key)
            response = client.models.generate_content(
                model=m_name,
                contents=test_prompt
            )
            reply = response.text.strip()
            return {
                "success": True,
                "message": f"🔵 Gemini 연결 성공! 모델: '{m_name}' | 응답: '{reply}'"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Gemini 연결 실패 (모델: '{m_name}'): {e}"
            }
            
    else:
        return {
            "success": False,
            "message": f"⚠️ 알 수 없는 공급사('{provider}')입니다."
        }

def generate_llm_response(prompt: str, config: Dict[str, Any], image_list: Optional[List[Dict[str, Any]]] = None, source_url: str = "") -> str:
    """선택된 LLM 공급사(ChatGPT, Claude, Gemini) 및 설정된 모델/API Key별 호출 분기 처리"""
    llm_settings = config.get("llm_settings", {})
    active_provider = llm_settings.get("active_provider", "Gemini").lower()
    active_model = llm_settings.get("active_model", "")
    
    models = llm_settings.get("models", {})
    api_keys = llm_settings.get("api_keys", {})
    
    # 1. ChatGPT (OpenAI)
    if "chatgpt" in active_provider or "openai" in active_provider or "gpt" in active_model.lower():
        m_name = models.get("chatgpt") or active_model or "gpt-4o"
        api_key = api_keys.get("openai") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("LLM API KEY가 설정되지 않았습니다. (현재 선택된 엔진: ChatGPT)")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=m_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM API (ChatGPT) 호출 오류: {e}")
            
    # 2. Claude (Anthropic)
    elif "claude" in active_provider or "anthropic" in active_provider or "claude" in active_model.lower():
        m_name = models.get("claude") or active_model or "claude-3-5-sonnet-20241022"
        api_key = api_keys.get("anthropic") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("LLM API KEY가 설정되지 않았습니다. (현재 선택된 엔진: Claude)")
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=m_name,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"LLM API (Claude) 호출 오류: {e}")
            
    # 3. Google Gemini (기본값)
    else:
        m_name = models.get("gemini") or active_model or "gemini-2.5-flash"
        api_key = api_keys.get("google") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("LLM API KEY가 설정되지 않았습니다. (현재 선택된 엔진: Gemini)")
            
        target_model = m_name
        if "gemini-2.0" in target_model:
            target_model = "gemini-2.5-flash"
            
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            try:
                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt
                )
                return response.text
            except Exception as inner_e:
                if target_model != "gemini-1.5-flash":
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt
                    )
                    return response.text
                raise inner_e
        except Exception as e:
            raise RuntimeError(f"LLM API (Gemini) 호출 오류: {e}")

def extract_title_from_raw_llm(raw_text: str, default_title: str) -> str:
    """LLM의 출력 원문에서 <h1> 태그 또는 첫 단락의 제목 텍스트를 정밀 추출"""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", raw_text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        clean_t = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if clean_t:
            return clean_t
    lines = [line.strip() for line in raw_text.split("\n") if line.strip() and not line.strip().startswith("```")]
    if lines:
        clean_t = re.sub(r"<[^>]+>", "", lines[0]).strip()
        if len(clean_t) > 5:
            return clean_t
    return default_title

def get_image_src_url(img: Dict[str, Any]) -> str:
    """이미지 파일 경로를 Base64 Data URI로 변환"""
    filepath = img.get("filepath", "")
    if os.path.exists(filepath):
        try:
            import base64
            ext = os.path.splitext(filepath)[1].lower().replace(".", "")
            mime = "image/png" if ext == "png" else "image/jpeg" if ext in ["jpg", "jpeg"] else "image/webp"
            with open(filepath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{b64}"
        except Exception as e:
            print(f"Base64 image encode error: {e}")
    return img.get("filename", "")

def build_image_instructions(image_list: Optional[List[Dict[str, Any]]] = None) -> str:
    """DB에 등록된 이미지 라이브러리를 프롬프트 지침 문자열로 변환 (플레이스홀더 방식)"""
    if not image_list:
        return "[실사 이미지 라이브러리 안내]\n등록된 실사 이미지가 없습니다. 이미지 태그 생성을 생략하고 글 텍스트만 작성하라."

    img_items = []
    for img in image_list:
        img_id = img.get("id")
        desc = img.get("description", "씨제이씨협동조합 관련 이미지")
        cat = img.get("category", "일반")
        img_items.append(f"- [태그: [[CJC_IMAGE_{img_id}]]] (카테고리: {cat}) 이미지 설명: '{desc}'")

    return f"""[실사 이미지 라이브러리 (자동 문맥 매칭 삽입 필수 지침)]
아래에 제공된 조합의 실제 촬영 이미지 목록 중, 포스팅 소제목(<h2>) 및 본문 단락 문맥과 가장 일치하는 이미지를 2~4개 선별하여 해당 소제목 바로 다음 단락에 제공된 이미지 태그(예: [[CJC_IMAGE_1]])를 단독 줄로 그대로 작성하라.
- 사용할 수 있는 실사 이미지 데이터베이스:
{chr(10).join(img_items)}
"""

def inject_image_tags(raw_text: str, image_list: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, List[str]]:
    """LLM이 반환한 원문에 포함된 [[CJC_IMAGE_X]] 플레이스홀더를 본문 상단부터 순서대로 HTML 이미지 태그로 치환하고 파일 경로 목록 반환"""
    if not image_list or not raw_text:
        return raw_text, []

    # id -> img 매핑 생성
    img_map = {str(img.get("id")): img for img in image_list if img.get("id")}

    import re
    # 본문 내 플레이스홀더 출현 순서(Top-to-Bottom) 탐색
    matches = list(re.finditer(r'\[\[CJC_IMAGE_(\d+)\]\]', raw_text))
    
    used_paths = []
    result_text = raw_text

    for m in matches:
        placeholder = m.group(0)
        img_id_str = m.group(1)
        img = img_map.get(img_id_str)
        
        if img and placeholder in result_text:
            filepath = img.get("filepath", "")
            if filepath and os.path.exists(filepath):
                used_paths.append(filepath)
            src = get_image_src_url(img)
            desc = img.get("description", "씨제이씨협동조합 실사 이미지")
            img_html = f'<br><div style="text-align: center; margin: 25px 0;"><img src="{src}" alt="{desc}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></div><br>'
            result_text = result_text.replace(placeholder, img_html, 1)

    return result_text, used_paths

def generate_seo_article(article_title: str, article_content: str, source_url: str, image_list: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """[F-02] 정보성 SEO 글 생성 프롬프트 조합 및 LLM 호출 파이프라인 (제목, 본문, 이미지 경로 반환)"""
    config = load_config()
    persona = config.get("persona_guide", {}).get("system_persona", "씨제이씨협동조합 마케팅 에디터")
    facts_list = config.get("fact_database", {}).get("company_facts", [])
    facts_str = "\n".join([f"- {fact}" for fact in facts_list])
    
    whitelist = config.get("compliance", {}).get("whitelist_seo", [])
    whitelist_str = ", ".join(whitelist)
    
    blacklist_keys = list(config.get("compliance", {}).get("blacklist_map", {}).keys())
    blacklist_str = ", ".join(blacklist_keys)

    img_instr = build_image_instructions(image_list)
    
    prompt = PROMPT_TEMPLATE_A.format(
        system_persona=persona,
        fact_database=facts_str,
        whitelist_keywords=whitelist_str,
        source_url=source_url,
        blacklist_keys=blacklist_str,
        image_instructions=img_instr,
        article_title=article_title,
        article_content=article_content
    )
    
    try:
        raw_output = generate_llm_response(prompt, config, image_list=image_list, source_url=source_url)
    except Exception as e:
        return {"success": False, "error": str(e), "title": "", "content": "", "image_paths": []}

    raw_output_with_imgs, used_paths = inject_image_tags(raw_output, image_list)
    ai_title = extract_title_from_raw_llm(raw_output, default_title=article_title)
    
    # 의료법 및 금기어 치환 + 네이버 에디터 포맷터 통과
    final_output = sanitize_compliance(raw_output_with_imgs, config)
    
    # 본문 내 어설픈 LLM 출처 텍스트 제거 후, 하단에 100% 클릭 가능한 원문 기사 출처 링크 보장 추가
    if source_url:
        final_output = re.sub(r'<p[^>]*>\s*\[?원문\s*기사\s*출처.*?<\/p>', '', final_output, flags=re.IGNORECASE | re.DOTALL)
        final_output = re.sub(r'\[?원문\s*기사\s*출처.*?(?:\]|\n|<|$)', '', final_output, flags=re.IGNORECASE)
        final_output += f'<br><p style="color: #888888; font-size: 13px; margin-top: 25px; border-top: 1px solid #eeeeee; padding-top: 10px;">📌 <strong>원문 기사 출처:</strong> <a href="{source_url}" target="_blank" rel="noopener noreferrer" style="color: #03c75a; text-decoration: underline;">{source_url}</a></p>'
        
    return {"success": True, "title": ai_title, "content": final_output, "image_paths": used_paths}

def generate_brand_expansion_article(post_category: str, post_outline: str, image_list: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """[F-03] 개요 기반 브랜드 글 확장 프롬프트 조합 및 LLM 호출 파이프라인 (제목, 본문, 이미지 경로 반환)"""
    config = load_config()
    persona = config.get("persona_guide", {}).get("system_persona", "씨제이씨협동조합 브랜드 디렉터")
    samples = config.get("persona_guide", {}).get("few_shot_samples", [])
    
    samples_str = ""
    for idx, s in enumerate(samples, 1):
        samples_str += f"--- [샘플 {idx}: {s.get('title', '')}] ---\n{s.get('content', '')}\n\n"

    img_instr = build_image_instructions(image_list)
        
    prompt = PROMPT_TEMPLATE_B.format(
        system_persona=persona,
        few_shot_samples=samples_str,
        post_category=post_category,
        post_outline=post_outline,
        image_instructions=img_instr
    )
    
    try:
        raw_output = generate_llm_response(prompt, config, image_list=image_list)
    except Exception as e:
        return {"success": False, "error": str(e), "title": "", "content": "", "image_paths": []}

    raw_output_with_imgs, used_paths = inject_image_tags(raw_output, image_list)
    default_t = f"[{post_category}] 씨제이씨협동조합 안내"
    ai_title = extract_title_from_raw_llm(raw_output, default_title=default_t)
    
    final_output = sanitize_compliance(raw_output_with_imgs, config)
    return {"success": True, "title": ai_title, "content": final_output, "image_paths": used_paths}

def generate_mock_fallback(prompt: str, model_name: str, error_msg: str, image_list: Optional[List[Dict[str, Any]]] = None, source_url: str = "") -> str:
    """API 키 미설정 또는 오류 발생 시 PoC 데모용 고품질 예시 원고 반환"""
    config = load_config()
    facts = config.get("fact_database", {}).get("company_facts", [])
    fact_sample = facts[0] if facts else "ATUM 3D 두상측정기 10분 정밀 스캔"

    placeholders = []
    if image_list:
        for img in image_list:
            placeholders.append(f"[[CJC_IMAGE_{img['id']}]]")

    img_ph1 = placeholders[0] if len(placeholders) > 0 else ""
    img_ph2 = placeholders[1] if len(placeholders) > 1 else ""
    img_ph3 = placeholders[2] if len(placeholders) > 2 else ""

    mock_body = f"""<h1>AI 시대의 탈모 고민, 이제는 씨제이씨협동조합의 3D 맞춤가발 키노피스로 혁신적인 케어를!</h1>

<p>안녕하세요! 사단법인 대한가발협회 소속 회원들이 뜻을 모아 설립한 <strong>씨제이씨협동조합(CJC Cooperative)</strong>입니다. 최근 탈모 고민이나 항암 치료 과정에서 맞춤가발 및 항암가발을 찾는 분들이 꾸준히 늘어나고 있습니다. 하지만 기존 가발 제작 방식은 석고나 비닐을 머리에 쓰고 본을 뜨느라 심각한 불편을 겪어야 했고, 제작부터 배송까지 한 달 이상의 긴 시간을 기다려야 하는 부담이 컸습니다.</p>

<h2>1. 60년 전통 가발 산업의 디지털 대전환(AX): ATUM 3D 두상측정기</h2>
{img_ph1}
<p>씨제이씨협동조합은 이러한 산업적 한계를 극복하기 위해 혁신적인 스마트 팩토리 인프라를 구축하였습니다. <strong>{fact_sample}</strong> 기술을 활용하여, 이제는 고객이 매장에 방문하여 단 10분 만에 두상과 탈모 형태를 오차 없이 정밀 스캔합니다. 석고 폐기물이 발생하지 않는 친환경(ESG) 공정을 실현하였으며, 제작 기간 역시 기존 1개월에서 <strong>7일~10일 수준으로 획기적으로 단축</strong>시켰습니다.</p>

<h2>2. KOTITI 인증 안전 브랜드 '키노피스(KINO PIECE)'</h2>
{img_ph2}
<p>두피가 민감하신 탈모 환우분들이나 항암 치료 고객님들을 위해 접착제와 제품 내 유해 물질을 엄격히 통제합니다. 공인시험기관 KOTITI 검사를 통해 폼알데하이드(20 mg/kg 이하) 및 톨루엔(1,000 mg/kg 이하) 등 독성 성분을 완벽히 통제한 친환경 맞춤가발을 공급하여 건강한 두피 관리를 선사해 드립니다.</p>

<h2>3. 소상공인 상생 및 가발 창업·두피 창업 교육</h2>
{img_ph3}
<p>저희 협동조합은 가발공장 OEM 연동과 가발창업, 두피창업교육 프로그램을 통해 일선 매장을 운영하시는 소상공인분들과 예비 창업자분들의 성장을 든든하게 조력하고 있습니다. 중소벤처기업부 장관상 및 고용노동부 사회적기업 인증으로 검증된 기술력과 상생의 가치를 직접 경험해 보세요.</p>
"""
    return mock_body

# 시맨틱 유사도 검증 템플릿 (기획 문서[F-01] 2차 검증 로직)
SEMANTIC_DUPLICATE_TEMPLATE = """
당신은 텍스트 유사도 분석 전문가입니다. 아래 두 기사의 요약본을 분석하여 의미적 중복(Semantic Duplicate) 여부를 판단하세요.

[기사 A]
제목: {title_a}
요약: {summary_a}

[기사 B]
제목: {title_b}
요약: {summary_b}

판단 기준:
1. 동일한 사건이나 주제를 다루는지
2. 정보의 내용이 80% 이상 겹치는지
3. 단순히 제목이나 출처만 다른 것이 아닌지

결과 형식:
중복여부: [예/아니오]
유사도: [0~100%]
이유: [한 문장 설명]
"""

def check_semantic_duplicate(article_a: Dict[str, Any], article_b: Dict[str, Any]) -> Dict[str, Any]:
    """LLM을 활용한 시맨틱 유사도 2차 검증 (기획 문서 [F-01] 구현)"""
    config = load_config()

    prompt = SEMANTIC_DUPLICATE_TEMPLATE.format(
        title_a=article_a.get("title", ""),
        summary_a=article_a.get("summary", ""),
        title_b=article_b.get("title", ""),
        summary_b=article_b.get("summary", "")
    )

    try:
        response = generate_llm_response(prompt, config)

        # 응답 파싱
        is_duplicate = "예" in response or "YES" in response.upper() or "true" in response.lower()
        similarity_score = 0

        # 유사도 점수 추출 시도
        import re
        score_match = re.search(r'(\d+)%', response)
        if score_match:
            similarity_score = int(score_match.group(1))

        return {
            "is_duplicate": is_duplicate,
            "similarity_score": similarity_score,
            "reason": response.strip()
        }
    except Exception as e:
        print(f"시맨틱 유사도 검증 실패: {e}")
        return {
            "is_duplicate": False,
            "similarity_score": 0,
            "reason": f"검증 실패: {e}"
        }


# =============================================================================
# 수동 수정 원고 LLM AI 종합 검토 및 Audit [고도화 기능]
# =============================================================================
AUDIT_ARTICLE_TEMPLATE = """
당신은 네이버 블로그 SEO 전문가이자 대한민국의 의료법 및 표시광고법 컴플라이언스 전문가입니다.
사용자가 수동으로 수정한 씨제이씨협동조합(CJC)의 블로그 원고를 종합적으로 검토 및 평가하세요.

[원고 제목]
{title}

[원고 본문 (HTML)]
{content}

[씨제이씨협동조합 컴플라이언스 가이드라인]
1. 과대광고/의료법 위반 금지어: "탈모 완치", "완벽 치료", "부작용 0%", "100% 모발 재생" 등 과장/의료 효능 표현 절대 금지. (대신 "두피 환경 개선", "스타일 보완", "맞춤가발 연출" 사용)
2. CJC 핵심 팩트 DB: ATUM 3D 디지털 스캐너(두피 3D 입체 측정), 7~10일 빠른 납기, KOTITI 유해물질 미검출 인증(키노피스), 가발창업 및 두피전문 교육 프로그램.
3. 네이버 블로그 SEO 규칙: 소제목 사용, 가독성 높은 문단 구성, 과도한 키워드 반복 어뷰징 지양.

[요청 사항]
반드시 다음 JSON 형식으로만 응답하세요. 다른 설명이나 텍스트는 포함하지 마세요:
{{
  "score": 90,
  "compliance_pass": true,
  "good_points": [
    "핵심 키워드가 자연스럽게 수록되었습니다.",
    "소제목 구분이 명확하여 가독성이 높습니다."
  ],
  "improvements": [
    "본문 중 의료법 위반 표현이 포함되지 않아 양호합니다."
  ],
  "suggested_title": "AI 최적화 교정 제목",
  "suggested_content": "AI 교정 본문 HTML"
}}
"""

def audit_edited_article(title: str, content: str) -> Dict[str, Any]:
    """사용자가 수동 편집한 원고의 SEO/가독성/의료법 위반 여부를 LLM AI로 검수하고 친절한 한국어 리포트 생성"""
    config = load_config()
    blacklist_map = config.get("compliance", {}).get("blacklist_map", {})
    
    import json, re
    
    # 1. 의료법/표시광고법 핵심 정규표현식 및 하드코딩 금지 패턴 검사
    medical_patterns = [
        (r'완벽한?\s*탈모\s*치료', '맞춤가발을 통한 스타일 보완'),
        (r'완벽한?\s*치료', '스타일 개선 및 보완'),
        (r'탈모\s*치료', '맞춤가발 스타일 보완'),
        (r'탈모\s*완치', '두피 환경 개선 및 스타일 보완'),
        (r'치료가?\s*가능', '스타일 보완 가능'),
        (r'완치가?\s*가능', '두피 보완 가능'),
        (r'모발\s*(영구\s*)?재생', '건강한 두피 관리'),
        (r'발모\s*효능', '두피 케어 도움'),
    ]
    
    found_violations = []
    full_text = f"{title} {content}"
    
    # 정규표현식 매칭 검사
    for pattern, replacement in medical_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            matched_word = match.group(0)
            if not any(matched_word == v[0] for v in found_violations):
                found_violations.append((matched_word, replacement))
                
    # config blacklist_map 단어 매칭 검사
    for forbidden, replacement in blacklist_map.items():
        if forbidden in full_text:
            if not any(forbidden == v[0] for v in found_violations):
                found_violations.append((forbidden, replacement))
            
    sanitized_title = sanitize_compliance(title, config)
    sanitized_content = sanitize_compliance(content, config)
    
    prompt = AUDIT_ARTICLE_TEMPLATE.format(
        title=title,
        content=content
    )
    
    parsed_dict = None
    try:
        raw_res = generate_llm_response(prompt, config)
        if raw_res and not raw_res.startswith("참고: 현재"):
            clean_str = re.sub(r'```json\s*', '', raw_res)
            clean_str = re.sub(r'```\s*$', '', clean_str).strip()
            json_match = re.search(r'\{.*\}', clean_str, re.DOTALL)
            if json_match:
                parsed_dict = json.loads(json_match.group(0), strict=False)
    except Exception as e:
        print(f"LLM Audit JSON Parsing Fallback: {e}")

    # LLM 응답이 있는 경우에도 의료법 위반 단어가 검출되면 무조건 위반(Pass=False)으로 보정
    if parsed_dict and isinstance(parsed_dict, dict) and "score" in parsed_dict:
        if found_violations:
            parsed_dict["compliance_pass"] = False
            parsed_dict["score"] = min(parsed_dict.get("score", 75), 70)
            v_list = [f"'{f}' ➔ '{r}'" for f, r in found_violations]
            warn_msg = f"⚠️ 의료법/표시광고법 위반 표현 감지: {', '.join(v_list)}"
            if warn_msg not in parsed_dict.get("improvements", []):
                parsed_dict.setdefault("improvements", []).insert(0, warn_msg)
                
        if "suggested_title" in parsed_dict:
            parsed_dict["suggested_title"] = sanitize_compliance(str(parsed_dict.get("suggested_title", "")), config)
        if "suggested_content" in parsed_dict:
            parsed_dict["suggested_content"] = sanitize_compliance(str(parsed_dict.get("suggested_content", "")), config)
        return parsed_dict

    # 룰 기반 리포트 생성 (LLM 렌더링 실패 또는 MOCK 동작 시)
    if found_violations:
        compliance_pass = False
        score = 70
        v_list = [f"'{f}' ➔ '{r}'" for f, r in found_violations]
        improvements = [
            f"⚠️ 의료법 및 표시광고법 위반 표현 감지: {', '.join(v_list)}",
            "💡 가발 및 두피 스타일링은 의학적 치료가 아니므로 '치료/완치' 표현 사용 시 게시물 정지 리스크가 있습니다."
        ]
        good_points = [
            "CJC 브랜드 톤앤매너 및 문사 가독성 유지",
            "3D 스캐너 등 기술적 팩트 구성 우수"
        ]
    else:
        compliance_pass = True
        score = 95
        good_points = [
            "✅ 의료법 및 표시광고법 위반 금지어(치료/완치 등)가 없어 매우 안전합니다.",
            "✅ 네이버 C-Rank/DIA+ SEO 지침에 맞는 브랜드 톤앤매너가 잘 유지되었습니다.",
            "✅ 소제목 및 핵심 팩트(ATUM 3D 스캐너, KOTITI 인증 등)가 명확하게 구성되어 있습니다."
        ]
        improvements = [
            "💡 현재 원고의 완성도가 매우 뛰어납니다. 이대로 네이버 에디터 전송 및 발행을 진행하셔도 좋습니다.",
            "💡 모바일 가독성을 위해 문단 간격을 적절히 유지해 주세요."
        ]

    return {
        "score": score,
        "compliance_pass": compliance_pass,
        "good_points": good_points,
        "improvements": improvements,
        "suggested_title": sanitized_title,
        "suggested_content": sanitized_content
    }


# =============================================================================
# SEO 키워드 밀도 분석기, 자동 보정기 및 해시태그 패키지 생성기 [고도화 1. 🎯]
# =============================================================================

SEO_REBALANCE_TEMPLATE = """
당신은 네이버 블로그 SEO 노출 전문가입니다.
아래 블로그 원고는 화이트리스트 키워드 밀도가 부족하거나 불균형합니다.
원고의 문맥과 어조를 자연스럽게 유지하면서, 아래 필수 화이트리스트 키워드를 원고 전체(제목 및 본문)에 걸쳐 총 단어 수 대비 3.0% ~ 5.0% 밀도가 되도록 자연스럽게 보정하여 재작성하세요.

[필수 화이트리스트 키워드]
{whitelist_keywords}

[의료법 준수 필수 수칙]
'치료', '완치', '재생' 등 의학적 효과 오인 표현은 절대 금지하며 '스타일 보완', '두피 케어', '스타일 개선'으로 유지할 것.

[기존 원고 제목]
{title}

[기존 원고 본문 HTML]
{content}

[출력 형식 제한]
반드시 다음 JSON 형식으로만 반환하세요:
{{
    "rebalanced_title": "보정된 제목",
    "rebalanced_content": "보정된 본문 HTML"
}}
"""

def analyze_seo_keyword_density(title: str, content_html: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """네이버 C-Rank & DIA+ 노출 기준 SEO 키워드 밀도(3.0%~5.5%) 정량 분석"""
    if config is None:
        config = load_config()

    whitelist = config.get("compliance", {}).get("whitelist_seo", ["가발", "탈모", "맞춤가발", "항암가발", "남성가발", "두피케어", "3D두상측정", "ATUM", "키노피스"])
    
    # HTML 태그 제거하여 순수 텍스트 추출
    pure_body = re.sub(r'<[^>]+>', ' ', content_html)
    full_text = f"{title} {pure_body}".strip()
    
    words = [w for w in re.split(r'\s+', full_text) if w]
    total_word_count = len(words)
    total_char_count = len(full_text.replace(' ', ''))

    if total_word_count == 0:
        total_word_count = 1

    keyword_counts = {}
    total_keyword_matches = 0

    for kw in whitelist:
        count = len(re.findall(re.escape(kw), full_text, flags=re.IGNORECASE))
        keyword_counts[kw] = count
        total_keyword_matches += count

    density_pct = round((total_keyword_matches / total_word_count) * 100, 2)

    if density_pct < 2.0:
        status = "LOW"
        status_label = "⚠️ 키워드 밀도 부족 (SEO 노출 강화 권장)"
        status_color = "red"
    elif 2.0 <= density_pct <= 5.5:
        status = "OPTIMAL"
        status_label = "🟢 최적의 SEO 키워드 밀도 유지 (네이버 C-Rank/DIA+ 최적화)"
        status_color = "green"
    else:
        status = "HIGH"
        status_label = "⚠️ 키워드 밀도 과다 (어뷰징 감지 주의)"
        status_color = "orange"

    missing_keywords = [kw for kw, c in keyword_counts.items() if c == 0]
    present_keywords = {kw: c for kw, c in keyword_counts.items() if c > 0}

    return {
        "total_words": total_word_count,
        "total_chars": total_char_count,
        "total_keyword_matches": total_keyword_matches,
        "density_pct": density_pct,
        "status": status,
        "status_label": status_label,
        "status_color": status_color,
        "keyword_counts": keyword_counts,
        "present_keywords": present_keywords,
        "missing_keywords": missing_keywords
    }

def auto_rebalance_seo_keywords(title: str, content_html: str, config: Optional[Dict[str, Any]] = None) -> Tuple[str, str, Dict[str, Any]]:
    """1클릭 SEO 키워드 자동 보정기 (LLM 호출로 3~5% 최적 밀도 재구성)"""
    if config is None:
        config = load_config()

    whitelist = config.get("compliance", {}).get("whitelist_seo", ["가발", "탈모", "맞춤가발", "항암가발", "3D두상측정", "ATUM", "키노피스"])
    prompt = SEO_REBALANCE_TEMPLATE.format(
        whitelist_keywords=", ".join(whitelist),
        title=title,
        content=content_html
    )

    try:
        raw_res = generate_llm_response(prompt, config)
        clean_str = raw_res.strip()
        json_match = re.search(r'\{.*\}', clean_str, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0), strict=False)
            new_title = data.get("rebalanced_title", title)
            new_content = data.get("rebalanced_content", content_html)
        else:
            new_title, new_content = title, content_html
    except Exception as e:
        print(f"auto_rebalance_seo_keywords failed: {e}")
        new_title, new_content = title, content_html

    final_title = sanitize_compliance(new_title, config)
    final_content = sanitize_compliance(new_content, config)
    stats = analyze_seo_keyword_density(final_title, final_content, config)

    return final_title, final_content, stats

def generate_recommended_hashtags(title: str, content_html: str, config: Optional[Dict[str, Any]] = None) -> List[str]:
    """네이버 스마트에디터 [발행] 팝업 등록용 상위 노출 7~12개 AI 추천 해시태그 패키지 생성"""
    if config is None:
        config = load_config()

    whitelist = config.get("compliance", {}).get("whitelist_seo", ["가발", "탈모", "맞춤가발", "항암가발", "3D두상측정", "ATUM", "키노피스"])
    
    tags = ["#씨제이씨협동조합", "#CJC협동조합"]
    full_text = f"{title} {content_html}"

    for kw in whitelist:
        if kw in full_text and f"#{kw}" not in tags:
            tags.append(f"#{kw}")

    extra_candidates = ["#맞춤가발추천", "#두피케어", "#항암가발추천", "#3D두상스캔", "#친환경가발", "#키노피스", "#가발창업", "#남성가발"]
    for cand in extra_candidates:
        if len(tags) >= 10:
            break
        if cand not in tags:
            tags.append(cand)

    return tags[:10]


