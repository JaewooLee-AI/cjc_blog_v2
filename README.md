# 🚀 씨제이씨협동조합 AI 블로그 마케팅 자동화 시스템 v2.0

> **CJC Cooperative AI-Powered SEO Blog Automation System**  
> 사단법인 대한가발협회 주축 설립 **씨제이씨협동조합(CJC Cooperative)**의 소상공인과 실무자를 위한 맞춤형 **AI 블로그 SEO 원고 생성, 법률 검수(Audit) 및 반자동 포스팅 자동화 시스템**입니다.

---

## 📌 목차 (Table of Contents)

1. [시스템 개요 (Overview)](#-시스템-개요-overview)
2. [핵심 기능 (Key Features)](#-핵심-기능-key-features)
3. [시스템 아키텍처 (Architecture)](#-시스템-아키텍처-architecture)
4. [프로젝트 디렉토리 구조 (Directory Structure)](#-프로젝트-디렉토리-구조-directory-structure)
5. [설치 및 실행 가이드 (Installation & Setup)](#-설치-및-실행-가이드-installation--setup)
6. [기술적 특징 및 안티봇 메커니즘 (Technical Highlights)](#-기술적-특징-및-안티봇-메커니즘-technical-highlights)
7. [의료법 & 표시광고법 컴플라이언스 (Compliance Guidelines)](#-의료법--표시광고법-컴플라이언스-compliance-guidelines)

---

## 🌟 시스템 개요 (Overview)

본 시스템은 60년 정체된 가발/두피 산업의 디지털 대전환(AX)을 선도하는 **씨제이씨협동조합**의 기술 자산(ATUM 3D 두상스캐너, 키노피스 ESG 가발 등)을 바탕으로, 네이버 검색 알고리즘(C-Rank / DIA+)에 최적화된 마케팅 원고를 AI로 생성하고 네이버 스마트에디터 ONE에 안전하게 전송합니다.

* **최신 트렌드 수집**: 구글 뉴스 RSS 및 네이버 뉴스에서 실시간 가발/탈모/두피 트렌드를 크롤링
* **멀티 LLM 라우팅**: OpenAI ChatGPT(gpt-4o), Anthropic Claude(3.5 Sonnet), Google Gemini(2.5 Flash) 동적 연동
* **AI 원고 검수 (Audit)**: 의료법 및 표시광고법 위반어 자동 정밀 감지, 1클릭 AI 교정안 반영
* **실사 이미지 연동**: 등록된 CJC DB 이미지 라이브러리와 본문 상단 순서(Top-to-Bottom) 1:1 매핑 및 정밀 위치 교체
* **반자동 안전 발행**: Playwright Persistent Browser Session 및 OS Clipboard 인젝션을 통한 봇 차단 리스크 0% 실현

---

## ✨ 핵심 기능 (Key Features)

### 1. 🔍 트렌드 뉴스 기사 자동 수집 & $O(1)$ 중복 아카이빙
- **다중 소스 크롤링**: 국내 뉴스(구글 한국 + 네이버 뉴스) 및 해외 뉴스(구글 영어) 분리/통합 수집
- **관련성 배점 필터링**: 제목(3점)과 본문(1점) 내 키워드 출현 빈도 및 연관성 점수(2점 이상) 자동 선별
- **SQLite 해시 중복 차단**: 기사 URL SHA-256 해시 비교로 $O(1)$ 중복 기사 자동 아카이빙 및 제외
- **테스트 옵션 지원**: `🧪 중복허용(테스트용)` 체크박스를 통한 테스트 목적 재크롤링 지원

### 2. 📝 정보성 SEO 포스팅 & 1,500자 브랜드 글 확장
- **CJC Fact DB PPL 자연스러운 인용**: 
  - ATUM 3D 두상스캐너 (24개 센서, 10분 정밀 스캔)
  - KOTITI 안전 인증 키노피스(KINO PIECE) 친환경 가발
  - 획기적 배송 단축 (기존 1개월 ➔ 7~10일)
- **단문 키워드 원고 확장**: 2~3줄 개요 입력만으로 CJC 마케팅 페르소나 어조가 적용된 1,500자 완결 포스팅 자동 생성

### 3. ✏️ 원고 수동 수정, 미리보기 & 1-Click AI 재검토 (AI Audit Engine)
- **4대 서브 탭 통제**:
  - `👁️ 렌더링 미리보기`: 최종 블로그 포스팅 실시간 렌더링 화면
  - `✏️ 원고 수정 및 AI 재검토`: 제목/본문 HTML 직접 수정, `[🤖 AI 재검토 요청]`, 품질 점수 카드(Good Points, Improvements) 및 `[✨ AI 추천 교정 원고 1클릭 반영]`
  - `🖼️ 첨부 이미지 교체 및 삭제`: 등록된 DB 이미지 라이브러리 드롭다운 교체 및 원고 삭제
  - `📄 HTML 소스 코드`: 정제된 최종 HTML 코드 제공

### 4. 🖼️ 등록 실사 이미지 라이브러리 & 본문 위치 정밀 교체
- **본문 출현 순서 매핑 (Top-to-Bottom)**: AI가 본문에 임의 배치한 이미지를 상단 출현 순서대로 `📷 이미지 #1`, `📷 이미지 #2` 1:1 매핑
- **N번째 태그 위치 정밀 치환**: `replace_nth_image_in_html` 및 `delete_nth_image_in_html` 알고리즘을 적용하여 본문 내 정확한 위치의 `<img>` 태그만 100% 정밀 교체/삭제

### 5. 🚀 네이버 스마트에디터 ONE 안전 전송 (Playwright & OS Clipboard)
- **Persistent Context 로그인 유지**: 기존 사용자 브라우저 쿠키/세션을 재활용하여 CAPTCHA 및 계정 잠금 무력화
- **OS 레벨 HTML 클립보드 인젝션**: Windows CF_HTML / macOS Pasteboard 바이너리 바인딩으로 스마트에디터 서식 깨짐 및 태그 유실 완전 차단
- **인간 지연 시뮬레이션**: 랜덤 타이핑 및 타이밍 인터벌(`time.sleep(random.uniform(0.1, 0.3))`) 적용
- **반자동(Semi-Auto) 포스팅**: 에디터에 제목/본문을 자동 작성한 후 브라우저를 띄워두고 수동 [발행]을 유도하여 100% 안전성 보장

### 6. ⚙️ 관리자 설정 (Admin Settings)
- **멀티 AI 모델 관리**: ChatGPT, Claude, Gemini 중 활성 엔진 선택 및 실시간 API 연결 테스트
- **의료법 금기어 사전 데이터 에디터 (`st.data_editor`)**: '완치', '치료' 등 금기어 및 추천 교정어 라이브러리 실시간 편집 및 `config.json` 동기화
- **실사 이미지 등록 관리**: 컴퓨터 내 이미지 파일 업로드 및 AI 문맥 매칭용 상세 설명/카테고리 관리

---

## 🏗️ 시스템 아키텍처 (Architecture)

```mermaid
flowchart TD
    A[뉴스 기사 / 트렌드 수집 crawler.py] -->|URL Hash O(1) 중복 검사| B[(SQLite DB db_manager.py)]
    A --> C[Multi-LLM Router llm_router.py]
    C -->|Gemini / ChatGPT / Claude| D[CJC Fact DB & Persona 주입]
    D --> E[의료법 & 표시광고법 Sanitizer]
    E --> F[Streamlit UI app.py]
    F -->|사용자 수동 편집 & AI Audit| G[LLM AI 원고 검수 리포트]
    F -->|1클릭 반영 / 이미지 교체| H[OS Clipboard Injector clipboard_manager.py]
    H -->|CF_HTML / macOS Pasteboard| I[Playwright Publisher naver_publisher.py]
    I -->|인간 유사 반자동 전송| J[네이버 블로그 스마트에디터 ONE]
```

---

## 📂 프로젝트 디렉토리 구조 (Directory Structure)

```
cjc_blog_v2/
├── app.py                     # Streamlit 기반 통합 메인 Web UI (Tab 1 ~ Tab 4)
├── crawler.py                 # 구글 뉴스 RSS / 네이버 뉴스 트렌드 크롤러 & 필터
├── db_manager.py              # SQLite 기반 중복 확인, 로그 적재, 이미지 DB 관리자
├── llm_router.py              # ChatGPT, Claude, Gemini 멀티 라우터 & AI Audit 엔진
├── clipboard_manager.py       # OS 크로스플랫폼 (macOS / Windows) Rich HTML 클립보드 인젝터
├── naver_publisher.py         # Playwright Persistent Context 네이버 에디터 반자동 전송 모듈
├── paste_worker.py            # Windows/macOS 클립보드 백그라운드 워커 프로세스
├── logger.py                 # 시스템 통합 로깅 모듈
├── config.json                # AI 모델 설정, 브랜드 페르소나, 팩트 DB, 컴플라이언스 사전
├── requirements.txt           # Python 의존성 라이브러리 목록
├── AGENTS.md                  # Vibe Coding 마스터 규약 및 가이드라인
├── .gitignore                 # 보안 및 용량 관리를 위한 파일 제외 설정
└── uploaded_images/           # DB 실사 이미지 저장소
```

---

## 🛠️ 설치 및 실행 가이드 (Installation & Setup)

### 1. 사전 요구사항 (Prerequisites)
- **Python**: 3.9 이상 권장
- **OS**: macOS (Apple Silicon / Intel) 또는 Windows 10/11

### 2. 가상환경 구축 및 패키지 설치
```bash
# 저장소 클론
git clone https://github.com/JaewooLee-AI/cjc_blog_v2.git
cd cjc_blog_v2

# 파이썬 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 라이브러리 설치
pip install -r requirements.txt

# Playwright 브라우저 바이너리 설치
playwright install chromium
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```
* 실행 후 웹 브라우저에서 `http://localhost:8501` 접속

---

## 🛡️ 기술적 특징 및 안티봇 메커니즘 (Technical Highlights)

1. **Undetected Chromium & Persistent Session**:
   * 네이버 봇 감지 알고리즘(C-Rank / DIA+)을 완전 무력화하기 위해 기본 Webdriver 대신 Playwright의 `launch_persistent_context`를 사용합니다.
   * 사용자의 실제 크롬 쿠키 및 세션을 재활용하여 캡차(CAPTCHA) 로그인 절차 없이 안전하게 접근합니다.

2. **OS Clipboard 바인딩 (`CF_HTML`)**:
   * 네이버 스마트에디터 ONE(`.se-main-container`)은 일반 `send_keys` 입력 시 HTML 서식이 깨지거나 텍스트가 유실됩니다.
   * 본 시스템은 OS 내장 패스보드(macOS `osascript` / Windows `win32clipboard`)를 통해 표준 CF_HTML 규격으로 인젝션 후 `Cmd+V` / `Ctrl+V` 키 이벤트를 전송하여 서식을 100% 보존합니다.

3. **자동 번역 오역 방지 메타태그 적용**:
   * 크롬/엣지 브라우저의 자동 번역 기능이 한국어 UI 라벨(예: '중복', '초기화')을 '단독', '점프' 등으로 오역하지 않도록 `<meta name="google" content="notranslate" />` 태그를 적용했습니다.

---

## ⚖️ 의료법 & 표시광고법 컴플라이언스 (Compliance Guidelines)

가발 및 두피케어 브랜드는 의료기관이나 의약품이 아니므로 관련 법률(의료법 제56조 및 표시광고법)을 엄격히 준수해야 합니다.

| 위반 위험 단어 (Prohibited) | 안전한 대체 표현 (Compliant Replacement) |
| :--- | :--- |
| **탈모 완치 / 완벽한 탈모 치료** | 두피 환경 개선 및 맞춤가발을 통한 스타일 보완 |
| **탈모 치료 / 완벽 치료** | 맞춤가발 스타일 개선 및 보완 |
| **치료 가능 / 완치 가능** | 스타일 보완 가능 / 두피 케어 보완 |
| **모발 영구 재생** | 건강한 두피 관리 |
| **부작용 제로** | KOTITI 안전성 검증 완료 |

> 시스템의 **`⚙️ 관리자 설정 (Admin)` ➔ `4. SEO 키워드 & 의료법 준수 치환 사전`**에서 금기어 및 치환어 라이브러리를 언제든지 자유롭게 편집하고 동기화할 수 있습니다.

---

## 📄 라이선스 (License)

Copyright © 2026 **씨제이씨협동조합 (CJC Cooperative)**. All rights reserved.
