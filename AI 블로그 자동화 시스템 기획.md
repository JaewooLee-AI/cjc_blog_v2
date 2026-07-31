# **씨제이씨협동조합 맞춤형 'AI 블로그 SEO 및 자동 포스팅 시스템' 딥리서치 및 바이브 코딩 전사 기획(PRD/아키텍처) 명세서**

## **서론: 가발 산업의 기술적 한계와 씨제이씨협동조합의 인공지능 대전환(AX) 전략**

국내 가발 및 탈모 케어 시장은 꾸준한 성장을 거듭하여 1조 4,000억 원 이상의 규모를 형성하고 있으며, 글로벌 시장 역시 2034년까지 최대 163억 달러 규모로 팽창할 것으로 전망된다.1 그러나 이러한 양적 팽창에도 불구하고 산업의 기반을 이루는 제조 및 공급망은 지난 60년 동안 심각한 기술적 정체를 겪어왔다. 특히 고객의 두상을 측정하기 위해 석고나 비닐을 뒤집어쓰고 본을 뜨는 방식은 심각한 산업 폐기물을 양산할 뿐만 아니라, 수작업에 의존하는 노동 집약적 공정으로 인해 제품 제작부터 배송까지 평균 1개월 이상이 소요되는 구조적 비효율을 낳았다.\[1, 1\]  
이러한 산업적 한계를 극복하기 위해 2014년 사단법인 대한가발협회 소속 회원들이 주축이 되어 설립한 씨제이씨협동조합(CJC Cooperative)은 가발 산업의 디지털 대전환(DX)을 선도하고 있다.\[1, 1\] 조합은 고용노동부 사회적기업 인증, 벤처기업 인증 및 우수협동조합 중소벤처기업부장관상을 수상하며 기술력과 사회적 가치를 동시에 입증하였다.1 특히 씨제이씨협동조합이 자체 개발한 'ATUM 3D 두상측정기'는 24개의 초정밀 센서와 3D 스테레오 카메라, 내부 레이저 마커를 탑재하여 단 10분 이내에 고객의 두상과 탈모 형태를 오차 없이 스캔하는 혁신적인 하드웨어 자산이다.1 수집된 3D 데이터는 스마트미러 시스템의 시뮬레이션을 거쳐 작업지시서로 자동 변환되며, 클라우드 기반의 ERP(전사적 자원 관리) 및 MES(제조 실행 시스템)와 실시간으로 연동되어 공장에 전송된다.\[1, 1\] 이를 통해 석고 폐기물이 없는 친환경(ESG) 공정을 실현하였고, 제작 및 배송 기간을 7일에서 10일 수준으로 획기적으로 단축하는 성과를 거두었다.1 아울러 유통 브랜드인 '키노피스(KINO PIECE)'를 통해 공인시험기관 KOTITI와 협력, 접착제 내 폼알데하이드(20 mg/kg 이하) 및 톨루엔(1,000 mg/kg 이하) 등 유해 물질 함량을 엄격히 통제한 안전한 맞춤가발 및 항암가발을 시장에 공급하고 있다.\[1, 1\]  
본 명세서는 이러한 씨제이씨협동조합의 독보적인 하드웨어 및 제조 인프라를 바탕으로, 일선 매장을 운영하는 소상공인 조합원(사용자)들의 마케팅 역량을 극대화하기 위한 'AI 블로그 SEO 및 자동 포스팅 시스템'의 개념 증명(PoC) 기획 및 아키텍처를 정의한다. 2주(약 25시간 공수)라는 제한된 프로젝트 기간 내에 바이브 코딩(Vibe Coding) 방법론을 활용하여 즉시 작동하는 프로토타입을 구축하는 것을 목표로 한다.\[1, 1\] IT 기기에 익숙하지 않은 소상공인 사용자 환경을 고려하여 직관적인 웹 인터페이스를 설계하는 동시에, 네이버 블로그의 엄격한 어뷰징 탐지 알고리즘을 우회할 수 있는 반자동(Semi-Auto) 발행 워크플로우와 고급 클립보드 제어 기술을 포괄적으로 명세하였다.

## **1장. 소프트웨어 제품 요구사항 정의서 (PRD)**

본 장에서는 씨제이씨협동조합의 소상공인 상생 비전과 가발 산업의 AX(AI Transformation) 전환을 실현하기 위한 블로그 마케팅 자동화 시스템의 핵심 기능과 제품 요구사항을 정의한다. 전체 시스템은 무인 자동화가 초래할 수 있는 검색 엔진 페널티 리스크를 원천 차단하면서도 원고 작성에 소요되는 물리적 시간을 90% 이상 단축하는 데 집중한다.

* **제품 개요:** 소상공인 상생 및 가발 산업 AX 전환을 위한 블로그 마케팅 자동화 PoC.1  
* **기능 명세서:**  
  * \[F-01\] 뉴스/트렌드 수집 및 중복 배제 모듈: RSS/크롤링 연동 및 SQLite 기반 중복 URL 검사.  
  * \[F-02\] SEO 최적화 정보성 원고 생성 엔진: 출처 표기, 타깃 키워드 밀도 유지, 자사 기술(ATUM, 키노피스) 자연스러운 연계 PPL.1  
  * \[F-03\] 개요(Input) 기반 브랜드 포스팅 확장 엔진: 단문 입력 시 Few-Shot 샘플의 어조를 반영하여 1,500자 원고 확장.  
  * \[F-04\] 반자동 네이버 블로그 전송 모듈: Playwright/Selenium 기반으로 에디터에 제목/본문 임시저장 및 사용자 승인 대기.  
  * \[F-05\] 시각화 모니터링 대시보드: Google Sheets API를 활용한 실행 로그 적재 및 Looker Studio 연동 실시간 통계 차트 제공.1

### **1.1 뉴스 및 트렌드 수집과 중복 배제 모듈 \[F-01\]**

탈모 및 두피 관리 시장의 최신 동향을 파악하고 정보성 포스팅의 질적 수준을 담보하기 위해, 시스템은 국내외 주요 뉴스 포털과 전문 매거진, 논문 데이터베이스 등에서 데이터를 자동으로 수집하는 엔진을 탑재한다. 파이썬의 BeautifulSoup과 feedparser 라이브러리를 활용하여 RSS 피드 및 검색 API를 주기적으로 크롤링하며, 수집 대상 키워드는 가발, 탈모, Scalp Care 등 다국어 트렌드 키워드를 포함한다.1  
이 과정에서 가장 중요한 기술적 요구사항은 동일한 기사나 유사한 내용이 중복으로 블로그에 발행되는 것을 방지하는 무결성 검증이다. 단기 PoC 단계에서 무거운 관계형 데이터베이스(RDBMS)를 도입하는 것은 개발 리소스의 낭비를 초래하므로, Python에 내장된 경량화 데이터베이스인 SQLite를 활용하여 수집 데이터를 관리한다.1 시스템은 크롤링된 기사의 원문 URL을 해시화하여 article\_history 테이블과 대조하고, O(1)의 시간 복잡도로 1차 물리적 중복을 필터링한다. 이후 단순 URL 번역이나 기사 재배포로 인한 의미적 중복을 방지하기 위해 거대 언어 모델(LLM)을 호출하여 기존 데이터베이스 내 요약본과의 시맨틱 유사도를 평가하는 2차 검증 로직을 수행한다.

### **1.2 SEO 최적화 정보성 원고 생성 엔진 \[F-02\]**

수집된 원시 데이터는 단순한 번역이나 요약을 넘어, 씨제이씨협동조합의 브랜드 아이덴티티와 결합된 SEO(검색엔진 최적화) 포스팅으로 재탄생해야 한다. LLM 기반의 원고 생성 엔진은 다음과 같은 세부 규칙을 엄격하게 준수하여 작동하도록 설계된다.  
첫째, 타깃 키워드의 전략적 배치다. 네이버 검색 로직(C-Rank 및 DIA+ 알고리즘)에 부합하기 위해 맞춤가발, 항암가발, 남성가발, 탈모가발, 3D두상측정, ATUM, 키노피스, 가발창업, 두피창업교육, 가발공장OEM, 스마트팩토리가발 등 사전 승인된 화이트리스트(Whitelist) 키워드들을 원고의 제목, 서론, 본문, 결론에 걸쳐 최적의 밀도(약 3\~5%)로 분산 배치한다.\[1, 1\] 둘째, 기술적 제품 간접 광고(PPL)의 자연스러운 연계다. 수집된 외부 기사가 다루는 문제점(예: 기존 맞춤 가발의 긴 제작 기간, 화학 물질로 인한 두피 트러블 등)을 서론에서 조명한 뒤, 해결책으로서 ATUM 3D 스캐너의 10분 정밀 측정 기능과 키노피스 브랜드의 KOTITI 인증(유해 물질 통제) 사실을 자연스러운 논리 구조로 인용하도록 프롬프트를 제어한다. 셋째, 출처 표기의 자동화다. 저작권 준수와 포스팅의 정보적 가치 신뢰도를 높이기 위해, 원고 하단에 반드시 원문 기사의 링크와 인용 출처를 양식화하여 포함시킨다.  
특히 의료법 및 표시광고법 위반 리스크를 통제하는 것은 시스템 설계에서 가장 중요한 비즈니스 요구사항 중 하나다. 가발 및 두피 관리 산업은 의학적 치료로 오인될 수 있는 과장 광고에 매우 취약하다.\[1, 1\] 따라서 시스템은 LLM이 생성한 원고 텍스트를 최종 출력하기 전에 블랙리스트(Blacklist) 정규표현식 파이프라인을 통과시킨다. 탈모 완치, 모발 영구 재생, 100% 치료, 병원 치료 대체, 의학적 효능, 부작용 제로 등의 금기어가 탐지될 경우, 시스템은 이를 자동으로 탈모 보완, 두피 케어, 스타일 개선, 안전성 검증 완료 등의 적법하고 안전한 용어로 강제 치환(Replace) 처리한다.

### **1.3 개요(Input) 기반 브랜드 포스팅 자동 확장 엔진 \[F-03\]**

단순 정보성 글 외에도 조합 및 매장의 실질적인 운영을 위한 공지사항과 마케팅 홍보 글을 작성하는 기능이 요구된다. 현업에 종사하는 소상공인분들은 긴 글을 작성할 시간적 여유가 부족하므로, 단 몇 줄의 핵심 개요(예: "추석 휴무 안내 9월 15일\~18일", "가발 창업반 4기 모집 선착순 10명")만 텍스트 박스에 입력하면 시스템이 이를 조합의 톤앤매너에 맞춘 1,500자 내외의 정식 원고로 확장(Expansion)하는 엔진을 구축한다.\[1, 1\]  
이 엔진은 타깃 오디언스의 성격에 따라 차별화된 Few-Shot 프롬프팅 기법을 적용한다. B2C 고객(탈모 및 맞춤가발 잠재 고객)을 대상으로 할 때는 따뜻한 공감과 위로를 바탕으로 ATUM 측정기의 정밀함과 친환경 공정의 신뢰감을 강조하는 페르소나를 취한다. 반면, B2B 고객(창업 희망자 및 타 소상공인)을 대상으로 할 때는 60년 전통 산업의 혁신을 이끄는 리더로서의 비전, 데이터 기반의 공신력, 그리고 협동조합을 통한 상생의 가치를 논리적으로 강조하는 어조를 유지한다.\[1, 1\] 시스템은 사전에 주입된 우수 포스팅 샘플을 참조하여 텍스트의 구조와 문단을 배열한다.

### **1.4 반자동 네이버 블로그 전송 모듈 (어뷰징 회피) \[F-04\]**

생성된 원고를 네이버 블로그에 등록하는 과정은 본 시스템에서 가장 고도의 기술적 정밀함이 요구되는 구간이다. 네이버는 2020년 5월부로 자동 광고성 포스팅을 근절하기 위해 공식 블로그 글쓰기 API의 지원을 완전히 종료하였다.1 따라서 시스템은 웹 브라우저 자동화 도구(Selenium 또는 Playwright)를 활용하여 실제 사람이 브라우저를 조작하는 것과 동일한 방식으로 스마트에디터 ONE에 접근해야 한다.1  
그러나 네이버의 안티 봇(Anti-bot) 시스템은 브라우저의 지문(Fingerprinting), navigator.webdriver 변수, 그리고 비정상적으로 빠른 입력 패턴을 실시간으로 감지하여 캡차(CAPTCHA)를 띄우거나 계정을 영구적인 저품질 상태로 전락시킨다.1 이를 우회하기 위해 본 시스템은 다음과 같은 3중 우회 아키텍처를 구현한다.  
첫째, 인증 세션의 보존이다. 프로그램이 매번 로그인 폼에 아이디와 비밀번호를 입력하는 행위는 봇 탐지의 주요 표적이 된다. 이를 방지하기 위해 undetected-chromedriver 패키지 또는 Playwright의 launch\_persistent\_context 기능을 사용하여, 사용자가 이미 정상적으로 로그인을 완료한 크롬 브라우저의 유저 데이터 프로필(User-Data Profile)과 쿠키를 그대로 로드한다.1 둘째, 스마트에디터 ONE의 클립보드 우회 인젝션이다. 스마트에디터 ONE은 동적 렌더링을 사용하는 React 기반의 복잡한 DOM 구조를 가지고 있어, send\_keys 메서드로 HTML 서식이 포함된 텍스트를 전송하면 태그가 깨지거나 입력이 거부된다.6 이를 해결하기 위해 Python의 win32clipboard 라이브러리를 통해 운영체제의 시스템 클립보드에 생성된 원고를 CF\_HTML (HTML Format) 규격으로 바인딩한 후, 에디터 영역을 클릭하고 ActionChain을 통해 Ctrl+V 키보드 이벤트를 발생시켜 인간의 복사-붙여넣기 행위를 완벽히 모사한다.9 셋째, 인간 유사 지연(Human Delay)의 강제 적용 및 반자동(Semi-Auto) 발행이다. 자동화된 프로세스는 제목, 본문 입력 및 '임시저장'까지만 수행하고 브라우저를 띄워둔 채 대기한다. 이후 사용자이 직접 화면을 검수하고 마우스로 \[발행\] 버튼을 클릭하게 함으로써, 네이버 시스템에 100% 정상적인 사용자의 행위로 인지되도록 설계한다.1

| 모듈명 | 주요 기술 스택 | 핵심 목적 및 제약 조건 |
| :---- | :---- | :---- |
| **뉴스/트렌드 수집** | BeautifulSoup, feedparser, sqlite3 | 최신 트렌드 확보 및 O(1) 복잡도의 로컬 URL 해시 중복 검증 수행 |
| **원고 생성 엔진** | LangChain, OpenAI API, Anthropic API | 타깃 키워드 주입 및 정규표현식 기반 의료법/광고법 금기어 치환(Sanitization) |
| **포스팅 확장 엔진** | LLM Prompting (Few-Shot) | B2C/B2B 페르소나 분리 및 입력된 단문 개요를 1,500자 브랜드 포스팅으로 확장 |
| **블로그 전송 모듈** | undetected-chromedriver, win32clipboard | 네이버 C-Rank/DIA+ 로직 우회를 위한 세션 재활용, CF\_HTML 클립보드 인젝션 및 반자동 발행 |
| **모니터링 대시보드** | Google Sheets, Looker Studio | 발행 이력 실시간 적재 및 시각적 통계(차트/스코어카드) 대시보드 링크 제공1 |

## **2장. 관리자 설정 대시보드(Admin UI) 및 동적 데이터 관리 명세**

씨제이씨협동조합의 비즈니스 환경과 가발 산업의 트렌드는 지속적으로 변화한다. 시스템의 영속성을 확보하기 위해 프롬프트, 팩트 데이터, 모델 키 등의 주요 변수를 소스 코드 내에 고정(Hard-coding)하는 것을 엄격히 배제한다. 대신, 프로그래밍 지식이 없는 소상공인 사용자과 조합 실무자들도 직관적으로 시스템의 두뇌를 제어할 수 있도록 Python Streamlit 프레임워크 기반의 \[⚙️ 관리자 설정\] 동적 대시보드를 제공한다.

### **2.1 관리자 대시보드 환경 및 파일 아키텍처**

초기 클라우드 배포(Vercel 등)를 고려할 경우 서버리스(Serverless) 환경 특성상 10\~60초의 함수 실행 타임아웃 제한이 발생하며, 이는 긴 시간이 소요되는 LLM 원고 생성 및 크롤링 작업에 치명적인 오류를 유발한다.1 따라서 본 시스템은 로컬 컴퓨터의 연산 자원을 활용하는 로컬 호스팅(Localhost) 방식 또는 PyInstaller를 통해 빌드된 독립 실행형 .exe 파일 형태로 납품된다.1 관리자 설정 탭에서 변경된 모든 데이터는 시스템 루트 디렉토리의 config.json 파일에 즉각적으로 동기화되어 저장되며, 보안을 위해 API 키와 같은 민감 정보는 암호화 처리 후 보관된다. 멀티 유저 간의 데이터 동기화가 필요할 경우, Google OAuth 2.0의 InstalledAppFlow 데스크톱 인증 방식을 적용하여 로컬에 token.json을 안전하게 생성한 뒤 Google Sheets API를 통해 데이터를 중앙 집중화하여 관리할 수 있도록 설계한다.15

### **2.2 관리자 대시보드 기능 명세**

> 1. **LLM 모델 및 API Key 관리 패널**: 특정 LLM 공급사의 서비스 장애나 비용 정책 변화에 유연하게 대응하기 위해 멀티 모델 라우팅을 지원한다. 사용자는 드롭다운 또는 라디오 버튼을 통해 Claude 3.5 Sonnet, GPT-4o, Gemini Pro 중 주력으로 사용할 모델을 자유롭게 스위칭할 수 있다.1 각 공급사별 API Key는 비밀번호 가림 처리(Password-type input)가 적용된 텍스트 박스를 통해 입력받는다.  
> 2. **AI 톤앤매너 & Few-Shot 샘플 동적 관리 패널**: AI의 글쓰기 어조를 결정짓는 핵심 패널이다. '브랜드 페르소나 가이드' 텍스트 영역을 제공하여, 필요 시 "친절하고 부드러운 사용자"에서 "전문적이고 신뢰감 있는 기술 컨설턴트"로 톤을 즉시 수정할 수 있다. 또한, 조합에서 반응이 좋았던 과거의 블로그 포스팅 원문을 텍스트 형태로 무제한 추가, 수정, 삭제(CRUD)할 수 있는 인터페이스를 제공하여 모델의 프롬프트 가이드라인(Few-Shot)을 동적으로 고도화한다.  
> 3. **조합 팩트 DB (RAG 지식고) 관리 패널**: AI가 거짓 정보(Hallucination)를 생성하는 것을 막고 제품 간접 광고(PPL)를 수행하기 위한 지식 베이스다. ATUM 3D 두상측정기의 업데이트된 스펙, 새로 획득한 KOTITI 품질인증 수치, 키노피스(KINO PIECE)의 신제품 라인업 등을 Bullet Point 형태로 추가하거나 수정할 수 있다.\[1, 1\] LLM은 원고 생성 시 반드시 이 패널에 기재된 팩트 중 1\~2가지를 글의 문맥에 맞게 인용하도록 강제된다.  
> 4. **SEO 키워드 & 금기어(Blacklist) 치환 단어장 관리 패널**: 네이버 검색 로직의 트렌드 변화에 대응하기 위해 타깃 키워드를 칩(Chip) UI 형태로 시각화하여 추가 및 삭제할 수 있도록 돕는다. 또한, 의료법 위반을 방지하는 블랙리스트 단어장은 Data Editor 위젯(테이블 형태)으로 구현하여 좌측 열에는 금기어(예: 탈모 완치)를, 우측 열에는 치환어(예: 스타일 개선)를 매핑하여 등록할 수 있게 한다.

### **2.3 동적 데이터 관리 JSON 스키마 (config.json)**

대시보드에서 제어되는 모든 상태 값은 다음과 같은 계층적 JSON 구조를 가지며 파이썬 백엔드와 상호작용한다.

| 최상위 Key | 하위 Key 및 데이터 타입 | 설명 및 기본값 예시 |
| :---- | :---- | :---- |
| llm\_settings | active\_model (String) api\_keys (Object) | 구동 모델 및 인증 정보. *예: "claude-3.5-sonnet-20241022"* |
| persona\_guide | persona\_desc (String) few\_shot\_samples (Array of Objects) | AI 페르소나 및 참조용 우수 포스팅 원문 리스트. *예:* |
| fact\_database | company\_facts (Array of Strings) | 포스팅에 강제 삽입될 조합의 기술 스펙 요약 리스트. *예:* |
| compliance | whitelist\_seo (Array of Strings) blacklist\_map (Object) | 검색 최적화 키워드 및 의료법 방지 치환 사전. *예: {"모발 영구 재생": "건강한 두피 관리"}* |

### **2.4 실시간 데이터 모니터링 대시보드 (Looker Studio 연동)**

시스템의 작동 현황을 한눈에 파악하기 위해, 별도의 무거운 웹 프론트엔드나 RDBMS를 구축하는 대신 구글 생태계를 활용한 직관적인 모니터링 대시보드를 제공한다.1

* **데이터 적재 (Google Sheets):** AI가 크롤링한 트렌드 기사 URL, 중복 검사 결과, 발행된 공지사항 및 포스팅 이력은 파이썬 백엔드에서 Google Sheets API를 통해 지정된 시트에 실시간으로 기록된다.1  
* **데이터 시각화 (Looker Studio):** 적재된 구글 시트 데이터를 구글의 무료 데이터 시각화 도구인 Looker Studio와 연동한다.1 이를 통해 '일자별 포스팅 발행 건수', '수집된 뉴스 카테고리 비중' 등을 대기업 보고서 수준의 화려한 그래프와 스코어카드로 표출한다.1 비개발자인 소상공인분들은 복잡한 데이터베이스 접속 없이, 공유받은 URL 링크 하나만으로 스마트폰과 PC에서 블로그 자동화 성과를 즉시 모니터링할 수 있다.1

## **3장. 사용자 매뉴얼 및 교육 지원 시스템 설계**

시스템의 궁극적인 성패는 최첨단 기술의 구현 유무가 아니라, 최종 사용자인 비개발자 소상공인분들이 이를 얼마나 거부감 없이 매일의 업무에 활용할 수 있느냐에 달려 있다. 따라서 별도의 두꺼운 PDF 매뉴얼을 배포하는 전통적 방식을 지양하고, 시스템 UI 내부에 교육 요소를 통합하는 직관적인 사용성 극대화 방안을 설계한다.\[1, 1\]

### **3.1 UI 내장형 대화형 가이드 (툴팁 명세)**

Streamlit 프레임워크의 help 인자를 적극 활용하여, 화면의 모든 입력 필드와 작동 버튼 옆에 물음표 모양의 아이콘을 배치하고 마우스 호버(Hover) 시 즉각적인 행동 지침을 제공하는 마이크로카피(Microcopy)를 구현한다.

* **\[개요 입력 텍스트 박스\]**: "💡 완벽한 문장으로 적지 않으셔도 됩니다. '가발 창업반 4기 모집', '선착순 10명', '다음 주 화요일 마감'처럼 전달하고 싶은 핵심 단어만 2\~3줄로 입력하시면 AI가 멋진 글로 살을 붙여줍니다."  
* **\[포스팅 유형 선택 드롭다운\]**: "💡 안내할 글의 성격(정보 제공, 휴무 안내, 이벤트 홍보 등)을 선택해 주세요. AI가 고객의 상황에 맞는 가장 적절한 말투로 문맥 조정합니다."  
* **\[블랙리스트 단어장 등록\]**: "💡 '완치', '치료' 등 의료법에 걸릴 수 있는 위험한 단어를 왼쪽 칸에, '케어', '보완' 등 안전한 단어를 오른쪽 칸에 적어두시면 AI가 글을 쓸 때 자동으로 교체해 줍니다."  
* **\[네이버 에디터로 전송 버튼\]**: "💡 버튼을 누르면 크롬 브라우저가 새로 열리고 사용자의 네이버 블로그에 글이 10초에 걸쳐 자동으로 입력됩니다. 화면이 멈출 때까지 마우스나 키보드를 절대 건드리지 마세요."

### **3.2 사용자 매뉴얼(User Guide) 자동 생성 마크다운 템플릿**

프로젝트 납품 시 씨제이씨협동조합의 실무자와 각 매장 소상공인분들에게 배포될 '10분 마스터 사용법' 문서의 초안이다. 이 문서는 시스템 디렉토리 내에 README.md 형식으로 내장되어 쉽게 열람할 수 있다.

# **🚀 씨제이씨협동조합 AI 블로그 마케팅 자동화 시스템 사용 가이드**

사용자님, 환영합니다\! 본 프로그램은 복잡한 조작 없이 마우스 클릭 몇 번만으로 우리 매장의 네이버 블로그를 전문가 수준으로 운영할 수 있도록 돕는 마법 같은 도구입니다. 네이버의 제재를 피하기 위해 가장 안전한 방식으로 설계되었습니다.

## **📌 3단계 초간단 사용법 (매일 10분만 투자하세요)**

### **1단계: 프로그램 켜기**

바탕화면에 있는 블로그\_자동화\_실행.exe 아이콘을 더블클릭합니다. 잠시 후 인터넷 창이 열리며 시스템 화면이 나타납니다.

### **2단계: 블로그 글 만들기 (2가지 방법 중 선택)**

* **\[해외/국내 트렌드 수집 탭\]**: 탈모나 가발에 관한 유익한 최신 정보를 올리고 싶을 때 사용합니다. 가발, 두피 관리 등의 단어를 적고 \[수집 시작\] 버튼을 누르면, AI가 관련 기사를 찾아 요약하고 우리 매장의 ATUM 3D 측정기 자랑을 덧붙여 훌륭한 정보성 글을 만들어냅니다.  
* **\[공지사항 및 홍보 작성 탭\]**: 우리 매장의 휴무일이나 할인 이벤트를 알리고 싶을 때 사용합니다. 메모장에 적듯 핵심 내용만 짧게 적어주시면, AI가 따뜻하고 친절한 사용자의 말투로 긴 글을 완성해 줍니다.

### **3단계: 안전하게 네이버 블로그에 올리기 (가장 중요\!)**

> 1. 화면에 AI가 쓴 글이 나타나면 한번 읽어보며 이상한 부분이 없는지 확인합니다.  
> 2. 하단의 파란색 **\[네이버 에디터로 전송\]** 버튼을 누릅니다.  
> 3. 시스템이 사용자의 네이버 블로그를 열고 제목과 본문을 예쁘게 붙여넣기 할 때까지 마우스를 가만히 둡니다.  
> 4. 입력이 끝나면, 네이버 화면 오른쪽 위의 초록색 **\[발행\]** 버튼을 사용자께서 '직접' 눌러주시면 모든 작업이 끝납니다. (기계가 자동으로 발행하면 네이버가 블로그를 차단할 수 있어, 안전을 위해 마지막 버튼은 사람이 직접 누르도록 설계되었습니다.)

## **4장. 바이브 코딩 에이전트 제어용 마스터 규칙**

최신 소프트웨어 개발 트렌드인 바이브 코딩(Vibe Coding)을 기업 환경에 적용할 때 가장 큰 리스크는 AI 에이전트(Cursor, Claude Code, Windsurf 등)가 프로젝트의 도메인 컨텍스트를 망각하거나 보안/제약 조건에 어긋나는 코문을 생성하는 것이다.1 이를 통제하기 위해 프로젝트 루트 디렉토리에 배치하여 에이전트의 사고와 코딩 패턴을 강제하는 AGENTS.md (또는 .cursorrules) 마스터 규약을 아래와 같이 명세한다.

# **CJC Cooperative Vibe Coding Master Rules (System Context)**

You are an expert Senior Python Developer, AI Architect, and Domain Specialist in the South Korean beauty and wig industry. You are currently building an SEO Blog Automation System for "CJC Cooperative (씨제이씨협동조합)". You MUST read and strictly adhere to the following rules for every single code generation, refactoring, or planning step. Failure to do so will break production and violate Korean internet compliance laws.

## **1\. Strict Workflow Enforcement (Research \-\> Plan \-\> Implement)**

Never generate large chunks of code immediately upon request. You must follow this strict 3-step lifecycle:

* **Research**: Before writing code, deeply analyze the existing file structure, config.json schema, and currently imported libraries (e.g., streamlit, win32clipboard, undetected-chromedriver).  
* **Plan**: Create a brief Markdown plan outlining exactly which files will be modified, what logical blocks will be injected, and how to prevent breaking existing components. Wait for human confirmation if modifying core architectural files.  
* **Implement**: Write concise, highly modular, and well-commented Python code. Ensure extreme robustness with try-except blocks.

## **2\. Naver Anti-Bot & Automation Bypassing Mechanics (CRITICAL)**

Naver operates aggressive anti-bot algorithms (C-Rank, DIA+, CAPTCHA).

* **NO Standard Selenium**: You must NEVER use the basic webdriver.Chrome(). You MUST utilize undetected-chromedriver or Playwright's chromium.launch\_persistent\_context to mask the navigator.webdriver and cdc\_ variables, and to reuse the user's existing browser cookie session to bypass login CAPTCHAs.  
* **Human-like Delay Enforcement**: You must always implement a random delay time.sleep(random.uniform(0.1, 0.3)) between any UI interactions (click, scroll, type).  
* **Rich Text Pasting via OS Clipboard**: Naver's SmartEditor ONE (.se-main-container) will break or strip HTML tags if you use the send\_keys method for rich text. You MUST use the win32clipboard module. You must strictly construct the CF\_HTML (HTML Format) payload containing precise byte-counted headers (Version:0.9, StartHTML, EndHTML, StartFragment, EndFragment). After registering the format and setting the clipboard data, use ActionChains to simulate Ctrl+V (or Cmd+V) inside the editor iframe.

## **3\. SQLite Modularization for Deduplication**

* Do not introduce heavy ORMs (like SQLAlchemy) for this PoC. Use the native sqlite3 library.  
* Abstract all database operations into a db\_manager.py file. Implement init\_db(), is\_article\_exists(url\_hash), and save\_article\_history(url\_hash, title) to handle O(1) deduplication of crawled news articles to prevent duplicate blog postings.

## **4\. Domain Context Injection & LLM Wrapper**

* **LLM Router Pattern**: Always route external API calls through a centralized llm\_router.py that dynamically reads the active model choice (Claude, OpenAI, Gemini) and API keys from config.json.  
* **System Prompt RAG Injection**: Whenever invoking an LLM for text generation, your python code MUST automatically load the CJC Fact DB (e.g., ATUM 3D Scanner, eco-friendly process, 7-10 days delivery, KOTITI certification) and the Persona from config.json, prepending them as System Prompts.  
* **Compliance Sanitization**: After receiving the LLM's output string, you MUST run a sanitization pipeline that replaces strictly prohibited medical terms listed in blacklist\_replacements (e.g., "탈모 완치" \-\> "두피 보완") BEFORE returning the final text to the UI.

## **5장. LLM 원고 생성용 파이썬 시스템 프롬프트 템플릿 (2종)**

파이썬 백엔드의 핵심 로직인 llm\_router.py 내부에 실제로 주입되어 작동할 시스템 프롬프트 템플릿이다. 하드코딩된 프롬프트가 아닌, 런타임 환경에서 config.json의 데이터가 파이썬의 f-string 메커니즘을 통해 동적으로 매핑되는 구조를 띤다.

### **5.1 해외/국내 트렌드 정보성 SEO 글 작성용**

외부에서 크롤링된 건조한 뉴스 기사를 씨제이씨협동조합의 고도화된 기술력을 홍보(PPL)하는 기회로 전환하며, 네이버 검색 노출 로직에 부합하도록 구조화하는 프롬프트이다.

Python  
PROMPT\_TEMPLATE\_A \= """  
너는 {system\_persona} 역할을 완벽하게 수행하는 수석 뷰티 에디터이자 마케팅 전문가다.  
아래에 제공된 외부 해외/국내 트렌드 뉴스의 핵심 정보를 파악하여, 네이버 블로그 검색 노출(SEO)에 최적화된 1,500자 이상의 양질의 정보성 포스팅 원고를 작성하라.

\[핵심 반영 및 구조화 지침\]  
1\. 서론 (공감 형성): 입력된 기사의 트렌드나 문제의식(예: 탈모 인구의 급증, 기존 가발의 화학물질 부작용 등)을 독자에게 친절하게 설명하며 고민에 깊이 공감하라.  
2\. 본론 (해결책 전환 및 브랜드 PPL): 외부 기사의 정보와 자연스러운 논리로 연결하여, 씨제이씨협동조합의 독보적인 기술 인프라가 완벽한 대안임을 강조하라.   
   \- 반드시 아래 제공된 우리 조합의 핵심 팩트(Fact DB) 중 2개 이상을 문맥에 맞게 인용할 것.  
   \-: {fact\_database}  
3\. SEO 타깃 키워드 배치: 글 전체(제목 포함)에 걸쳐 다음의 화이트리스트 키워드를 가장 자연스러운 형태로 3\~5회 분산 배치하라.  
   \- \[필수 키워드 목록\]: {whitelist\_keywords}  
4\. 출처 표기 자동화: 저작권과 공신력을 위해, 글의 마지막 단락에는 반드시 \[원문 기사 출처: {source\_url}\] 양식을 덧붙여라.  
5\. 금기어 정책 (법적 리스크 방지): 절대 의학적 치료 효과를 보장하거나 오인하게 만드는 단어({blacklist\_keys})를 사용하지 마라. 발견 즉시 보완, 케어 등의 단어로 우회하라.

\[입력된 외부 기사 데이터\]  
\- 기사 제목: {article\_title}  
\- 기사 본문 요약: {article\_content}

\[출력 형식 제한\]  
출력물은 순수한 텍스트가 아닌, 네이버 스마트에디터에 붙여넣었을 때 시각적으로 완성도를 띠도록 HTML 태그(\<h1\>, \<h2\>, \<p\>, \<strong\>, \<br\> 등)를 적극적으로 활용하여 포맷팅하라.  
"""

### **5.2 실무자 개요 입력 기반 브랜드 공지/마케팅 글 작성용**

소상공인 사용자이나 조합 실무자가 입력한 불완전하고 짧은 단문(개요)을 입력받아, 조합의 상생 비전과 브랜드 철학이 듬뿍 담긴 감성적이고 신뢰감 있는 장문의 포스팅으로 변환(Expansion)하는 프롬프트이다.

Python  
PROMPT\_TEMPLATE\_B \= """  
너는 {system\_persona} 역할을 수행하는 씨제이씨협동조합의 수석 브랜드 콘텐츠 디렉터다.  
아래 실무자가 입력한 거칠고 짧은 단어 중심의 개요(Outline)를 바탕으로, 타깃 고객과 소상공인분들의 마음을 사로잡는 따뜻하고 논리적인 1,500자 내외의 브랜드 공식 포스팅을 완성하라.

\[작성 및 톤앤매너 극대화 지침\]  
1\. 완벽한 톤앤매너 모방 (Few-Shot): 아래에 제공된 우리 조합의 과거 우수 포스팅 샘플을 심도 있게 분석하여, 그 특유의 어조, 높임말의 형태, 단락을 나누는 호흡을 100% 동일하게 모방하라.  
   \- \[우수 포스팅 참조 샘플\]: {few\_shot\_samples}  
2\. 도입부 비전 세팅: 60년 동안 정체되어 온 가발 산업을 혁신하는 '대한가발협회 소속 씨제이씨협동조합'의 철학(상생, 디지털 대전환, ESG 경영)을 가볍게 터치하며 신뢰감을 주면서 글을 시작하라.  
3\. 본문 확장 (Expansion): 실무자가 입력한 핵심 내용이 단 하나도 누락되어서는 안 되며, 무미건조한 단어들에 살을 붙여 고객이 이해하기 쉽도록 구체적이고 친절하게 풀어서 설명하라.   
4\. 결론 및 CTA (Call to Action): 독자가 글을 다 읽은 후 자연스럽게 가까운 조합 가맹점 방문을 예약하거나, 창업 교육 문의, 혹은 ATUM 3D 두상측정기 도입을 고려하도록 유도하는 부드러운 맺음말을 작성하라.

\[실무자 입력 데이터\]  
\- 포스팅 유형: {post\_category}  
\- 주요 전달 개요: {post\_outline}

\[출력 형식 제한\]  
네이버 에디터에 그대로 붙여넣을 수 있도록, 글의 제목은 \<h1\> 태그로 감싸고, 소제목은 \<h2\>, 본문 내 강조할 부분은 \<strong\> 태그를 사용하여 시각적으로 아름답게 구조화된 HTML 문서를 반환하라.  
"""

## **결론 및 아키텍처 요약**

본 기획 및 아키텍처 명세서는 단순한 API 연동을 통한 블로그 자동화를 넘어, 60년간 정체된 가발 산업을 디지털과 AI의 영역으로 끌어올리려는 씨제이씨협동조합의 거시적 비전을 소프트웨어 구조로 치환해 낸 청사진이다. 네이버 블로그 생태계 특유의 폐쇄적인 안티 봇 시스템과 에디터 서식 붕괴 문제를 undetected-chromedriver 기반의 세션 재활용과 win32clipboard의 정밀한 CF\_HTML 바인딩 기술로 완벽하게 극복하도록 설계되었다.1  
동시에 비개발자인 소상공인분들이 시스템의 심장부(프롬프트, 팩트 데이터, 모델 키)를 동적으로 제어할 수 있도록 Streamlit 기반의 로컬 대시보드와 직관적인 툴팁 가이드를 통합하였다.\[1, 1\] 본 명세서에 수록된 엄격한 PRD와 AGENTS.md 제어 규칙을 바이브 코딩 에이전트에 주입함으로써, 개발 팀은 2주라는 단기 스프린트 내에 어뷰징 페널티 리스크가 제로에 수렴하는 가장 안전하고 강력한 형태의 '반자동 AI 블로그 마케팅 프로토타입(PoC)'을 성공적으로 인도하게 될 것이다.

#### **참고 자료**

> 1. 씨제이씨협동조합\_중국AI.docx  
> 2. How to Scrape Naver.com: 2026 Python Guide \- Scrapfly Blog, 7월 27, 2026에 액세스, [https://scrapfly.io/blog/posts/how-to-scrape-naver](https://scrapfly.io/blog/posts/how-to-scrape-naver)  
> 3. Undetected Chromedriver: The Ultimate Guide to Bypassing Bot Detection in 2025, 7월 27, 2026에 액세스, [https://rebrowser.net/blog/undetected-chromedriver-the-ultimate-guide-to-bypassing-bot-detection](https://rebrowser.net/blog/undetected-chromedriver-the-ultimate-guide-to-bypassing-bot-detection)  
> 4. undetected ChromeDriver in Python: Avoid Bot Detection When Web Scraping \- Decodo, 7월 27, 2026에 액세스, [https://decodo.com/blog/undetected-chromedriver](https://decodo.com/blog/undetected-chromedriver)  
> 5. Using the Clipboard in Playwright: Copy, Paste, Automate \- SKPTRICKS \- Programmer Hub, 7월 27, 2026에 액세스, [https://www.skptricks.com/2025/04/using-clipboard-in-playwright-copy-and-paste.html](https://www.skptricks.com/2025/04/using-clipboard-in-playwright-copy-and-paste.html)  
> 6. 복사/붙여넣기 이용 방법 : 블로그 고객센터, 7월 27, 2026에 액세스, [https://help.naver.com/service/5593/contents/15544?osType=PC\&lang=ko](https://help.naver.com/service/5593/contents/15544?osType=PC&lang=ko)  
> 7. 이미지 붙혀넣기 · Issue \#85 · naver/smarteditor2 \- GitHub, 7월 27, 2026에 액세스, [https://github.com/naver/smarteditor2/issues/85](https://github.com/naver/smarteditor2/issues/85)  
> 8. 한글 파일에서 복사하여 에디터에 붙여 넣을 때 html태그에 대해 문의드립니다.(hwpEditorBoardContent) · Issue \#204 · naver/smarteditor2 \- GitHub, 7월 27, 2026에 액세스, [https://github.com/naver/smarteditor2/issues/204](https://github.com/naver/smarteditor2/issues/204)  
> 9. \[키홈\] Python selenium 자동화 cheat sheet \- 키홈의 챗GPT 머신러닝 자동화 블로그, 7월 27, 2026에 액세스, [https://kihome15.tistory.com/10](https://kihome15.tistory.com/10)  
> 10. Enumerate clipboard formats with Python and Pywin32 \- Github-Gist, 7월 27, 2026에 액세스, [https://gist.github.com/Rhomboid/5155189](https://gist.github.com/Rhomboid/5155189)  
> 11. win32clipboard.RegisterClipboardFormat \- Tim Golden, 7월 27, 2026에 액세스, [https://timgolden.me.uk/pywin32-docs/win32clipboard\_\_RegisterClipboardFormat\_meth.html](https://timgolden.me.uk/pywin32-docs/win32clipboard__RegisterClipboardFormat_meth.html)  
> 12. Python Copy gif to clipboard on windows \- GitHub Gist, 7월 27, 2026에 액세스, [https://gist.github.com/martinandersen3d/2de4d79641f71fdd34c8e92963ecd3ff](https://gist.github.com/martinandersen3d/2de4d79641f71fdd34c8e92963ecd3ff)  
> 13. Copy image to clipboard and preserve transparency \- Stack Overflow, 7월 27, 2026에 액세스, [https://stackoverflow.com/questions/66845295/copy-image-to-clipboard-and-preserve-transparency](https://stackoverflow.com/questions/66845295/copy-image-to-clipboard-and-preserve-transparency)  
> 14. python \- SetClipboardData can't write any data \- Stack Overflow, 7월 27, 2026에 액세스, [https://stackoverflow.com/questions/78473881/setclipboarddata-cant-write-any-data](https://stackoverflow.com/questions/78473881/setclipboarddata-cant-write-any-data)  
> 15. Setting up OAuth 2.0 \- API Console Help \- Google Help, 7월 27, 2026에 액세스, [https://support.google.com/googleapi/answer/6158849?hl=en](https://support.google.com/googleapi/answer/6158849?hl=en)  
> 16. streamlit/gsheets-connection \- GitHub, 7월 27, 2026에 액세스, [https://github.com/streamlit/gsheets-connection](https://github.com/streamlit/gsheets-connection)  
> 17. Authentication — gspread 6.2.1 documentation, 7월 27, 2026에 액세스, [https://docs.gspread.org/en/master/oauth2.html](https://docs.gspread.org/en/master/oauth2.html)