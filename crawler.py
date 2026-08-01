import requests
import feedparser
from bs4 import BeautifulSoup
import urllib.parse
import re
import warnings
from typing import List, Dict, Any, Tuple
import db_manager
import json
import os

warnings.filterwarnings("ignore")

# 다국어 뉴스 수집 키워드 (기획 문서대로 다국어 지원)
DEFAULT_KEYWORDS = {
    "ko": ["가발", "탈모", "맞춤가발", "두피케어", "항암가발", "가발제작", "인조가발", "남성가발"],
    "en": ["wig", "hair loss", "alopecia", "scalp care", "custom wig", "hair replacement", "toupee", "medical wig"]
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def is_korean_source(source: str, url: str) -> bool:
    """한국 출처 또는 한국 도메인인지 확인 (국내/해외 구분용)"""
    # 한국 언론사 목록
    korean_sources = [
        "연합뉴스", "YTN", "MBC", "SBS", "KBS", "채널A", "채널B", "JTBC", "TV조선",
        "동아일보", "조선일보", "중앙일보", "한겨레", "경향신문", "한국경제", "매일경제",
        "헤럴드경제", "머니투데이", "서울경제", "프라임경제", "네이버", "다음", "네이트",
        "MBN", "연합뉴스TV", "KNN", "kbc", "TBN", "한국경제TV", "내외경제", "이데일리",
        "지역신문", "전국매일신문", "스포츠서울", "서울신문", "경기일보", "인천일보",
        "아시아경제", "비즈니스워치", "브릿지경제", "파이낸셜뉴스", "워싱턴포스트",
        "뉴스1", "뉴시스", "헬스조선", "조선비즈", "아시아투데이", "전자신문", "디지털타임스",
        "스마트에프엔", "공공뉴스", "의학신문", "파이낸스뉴스", "한국일보", "세계일보",
        "국민일보", "데일리안", "아이뉴스24", "조선비즈", "지디넷", "메디칼타임즈"
    ]

    # 한국 도메인 패턴
    korean_domains = [
        ".co.kr", ".kr", ".or.kr", ".go.kr", ".ac.kr",
        "news.naver.com", "news.daum.net", "news.nate.com",
        "joins.com", "chosun.com", "donga.com", "hankooki.com",
        "khan.co.kr", "mk.co.kr", "sedaily.com", "mt.co.kr",
        "heraldcorp.com", "moneytoday.co.kr", "seoul.co.kr",
        "incheonilbo.com", "asiapress.co.kr", "bbn.co.kr"
    ]

    # 출처명 확인 (대소문자 무시)
    if any(k_source.lower() in source.lower() for k_source in korean_sources):
        return True

    # URL 도메인 확인
    if any(k_domain in url.lower() for k_domain in korean_domains):
        return True

    return False

def detect_korean_text(text: str) -> bool:
    """텍스트의 한글 비율이 50% 이상인지 확인"""
    if not text:
        return False

    korean_chars = len([char for char in text if '가' <= char <= '힣'])
    total_chars = len([char for char in text if char.isalpha()])

    if total_chars == 0:
        return False

    return (korean_chars / total_chars) >= 0.5

def translate_to_korean(text: str) -> str:
    """영어 텍스트를 한글로 자동 번역 (Google Translate API 또는 실패 시 원문 반환)"""
    if not text or not text.strip():
        return text

    # 이미 한글이 포함되어 있으면 번역 생략
    if detect_korean_text(text):
        return text

    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ko&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated_chunks = []
            if result and isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                for chunk in result[0]:
                    if chunk and isinstance(chunk, list) and len(chunk) > 0 and chunk[0]:
                        translated_chunks.append(chunk[0])
                if translated_chunks:
                    return "".join(translated_chunks)
    except Exception as e:
        print(f"Translation failed: {e}")

    return text

def translate_to_english(text: str) -> str:
    """한글 키워드를 영문 키워드로 자동 번역 (사전 매핑 + 구글 번역 API)"""
    if not text or not text.strip():
        return text

    # 알려진 주요 업계 키워드 사전 매핑
    dict_map = {
        "가발": "wig",
        "탈모": "hair loss",
        "맞춤가발": "custom wig",
        "두피케어": "scalp care",
        "항암가발": "medical wig",
        "가발제작": "wig manufacturing",
        "인조가발": "synthetic wig",
        "남성가발": "men toupee",
        "탈모가발": "hair loss wig",
        "3D두상측정": "3D head measurement",
        "두피창업교육": "scalp care education",
        "가발공장OEM": "wig factory OEM",
        "스마트팩토리가발": "smart factory wig"
    }
    if text in dict_map:
        return dict_map[text]

    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=en&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=4)
        if response.status_code == 200:
            result = response.json()
            if result and isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                translated = result[0][0][0].strip().lower()
                if translated:
                    return translated
    except Exception as e:
        print(f"Translation to English failed for '{text}': {e}")

    return text

def fetch_fallback_naver_scraping(keyword: str, max_results: int = 5, ignore_dedup: bool = False) -> List[Dict[str, Any]]:
    """[Fallback Web Scraper] Naver News HTML 수집 (RSS 장애/블록 시 예외 회피 파이프라인)"""
    search_url = f"https://search.naver.com/search.naver?where=news&query={urllib.parse.quote(keyword)}&sm=tab_opt&sort=0&photo=0&field=0"
    print(f"  🌐 [Fallback Web Scraper] Naver News HTML 직접 스크래핑 시도: '{keyword}'")

    try:
        response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=8)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Fallback Naver scraping failed for {keyword}: {e}")
        return []

    articles = []
    news_items = soup.select("div.news_wrap")[:max_results * 2]

    for item in news_items:
        try:
            title_tag = item.select_one("a.news_tit")
            if not title_tag:
                continue

            link = title_tag.get("href", "")
            title = title_tag.get_text(strip=True)

            if not link or not title:
                continue

            # 1차 O(1) URL 및 제목 해시 중복 검사
            if not ignore_dedup and db_manager.is_article_exists(link, title):
                continue

            summary_tag = item.select_one("div.news_dsc")
            summary = summary_tag.get_text(strip=True) if summary_tag else title

            source_tag = item.select_one("a.info.press")
            source = source_tag.get_text(strip=True) if source_tag else "Naver News (Web Scraper)"

            article_data = {
                "url": link,
                "title": title,
                "summary": summary,
                "source": f"{source} [WebScraper]",
                "published": "",
                "keyword": keyword,
                "language": "ko",
                "news_type": "domestic"
            }
            articles.append(article_data)
            if len(articles) >= max_results:
                break
        except Exception as e:
            print(f"Error parsing Fallback Naver item: {e}")
            continue

    return articles

def fetch_google_news_rss(keyword: str, language: str = "ko", max_results: int = 5, ignore_dedup: bool = False) -> List[Dict[str, Any]]:
    """구글 뉴스 RSS 피드에서 키워드 기반 최신 기사 수집 (다국어 지원 및 O(1) 해시 중복검사)"""
    if language == "ko":
        encoded_keyword = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    else:  # 영어권
        encoded_keyword = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en&gl=US&ceid=US:en"

    try:
        response = requests.get(rss_url, headers=DEFAULT_HEADERS, timeout=8)
        if response.status_code != 200:
            return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"Error fetching Google News RSS for {keyword} ({language}): {e}, switching to Fallback Scraper...")
        return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)

    articles = []

    # 충분한 미수집 기사를 확보하기 위해 상위 50개 항목 탐색
    for entry in feed.entries[:50]:
        link = entry.get("link", "")
        title = entry.get("title", "")
        published = entry.get("published", "")
        source = entry.get("source", {}).get("title", "Google News")

        if not link or not title:
            continue

        # 1차 O(1) URL 및 제목 해시 중복 검사
        if not ignore_dedup and db_manager.is_article_exists(link, title):
            continue

        # 국내/해외 구분 및 언어 필터링
        is_korean = is_korean_source(source, link)
        combined_text = f"{title} {entry.get('summary', '')}"
        has_korean_text = detect_korean_text(combined_text)

        if language == "en":
            if is_korean or has_korean_text:
                continue
        elif language == "ko":
            if not is_korean and not has_korean_text:
                continue

        summary_raw = entry.get("summary", "")
        soup = BeautifulSoup(summary_raw, "html.parser")
        clean_summary = soup.get_text(separator=" ").strip()
        if not clean_summary:
            clean_summary = title

        summary_ko = clean_summary
        summary_en_orig = ""
        if language == "en":
            summary_en_orig = clean_summary
            summary_ko = translate_to_korean(clean_summary)

        article_data = {
            "url": link,
            "title": title,
            "summary": summary_ko,
            "summary_original": summary_en_orig,
            "source": source,
            "published": published,
            "keyword": keyword,
            "language": language,
            "news_type": "domestic" if language == "ko" else "international"
        }
        articles.append(article_data)
        if len(articles) >= max_results:
            break

    # RSS 결과가 비어있는 경우 Fallback Web Scraper로 즉시 자동 릴레이 전환
    if not articles:
        print(f"⚠️ Google News RSS empty for '{keyword}', executing Fallback Web Scraper...")
        return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)

    return articles

def fetch_naver_news_search(keyword: str, max_results: int = 5, ignore_dedup: bool = False) -> List[Dict[str, Any]]:
    """네이버 뉴스 검색 크롤링 (O(1) 해시 중복검사 & Fallback 지원)"""
    search_url = f"https://search.naver.com/search.naver?where=news&query={urllib.parse.quote(keyword)}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=0&ds=&de=&docid=&nso=so%3Ar%2Cp%3Aall&mynews=0&refresh_start=0&related=0"

    try:
        response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=8)
        if response.status_code != 200:
            return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching Naver News for {keyword}: {e}, switching to Fallback Scraper...")
        return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)

    articles = []
    news_items = soup.select("div.news_wrap")[:max_results * 2]

    for item in news_items:
        try:
            title_tag = item.select_one("a.news_tit")
            if not title_tag:
                continue

            link = title_tag.get("href", "")
            title = title_tag.get_text(strip=True)

            if not link or not title:
                continue

            # 1차 O(1) URL 및 제목 해시 중복 검사
            if not ignore_dedup and db_manager.is_article_exists(link, title):
                continue

            summary_tag = item.select_one("div.news_dsc")
            summary = summary_tag.get_text(strip=True) if summary_tag else title

            source_tag = item.select_one("a.info.press")
            source = source_tag.get_text(strip=True) if source_tag else "Naver News"

            article_data = {
                "url": link,
                "title": title,
                "summary": summary,
                "source": source,
                "published": "",
                "keyword": keyword,
                "language": "ko",
                "news_type": "domestic"
            }
            articles.append(article_data)
            if len(articles) >= max_results:
                break
        except Exception as e:
            print(f"Error parsing Naver news item: {e}")
            continue

    if not articles:
        return fetch_fallback_naver_scraping(keyword, max_results, ignore_dedup)

    return articles

def check_article_relevance(article_data: Dict[str, Any], target_keywords: List[str]) -> Tuple[bool, float]:
    """기사 관련성 필터링: 키워드 빈도 및 문맥 분석"""
    title = article_data.get("title", "").lower()
    summary = article_data.get("summary", "").lower()
    combined_text = f"{title} {summary}"

    keyword_score = 0
    for keyword in target_keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title:
            keyword_score += 3
        if keyword_lower in summary:
            keyword_score += 1

    relevance_indicators = [
        "모발", "두피", "머리", "헤어", "샴푸", "케어", "살모", "헤어",
        "hair", "scalp", "wig", "toupee", "alopecia"
    ]

    relevance_score = 0
    for indicator in relevance_indicators:
        if indicator in combined_text:
            relevance_score += 0.5

    total_score = keyword_score + relevance_score
    is_relevant = total_score >= 2.0
    return is_relevant, total_score

import difflib

def quick_text_similarity(t1: str, t2: str) -> float:
    """로컬 빠른 문자열 유사도 계산 (무분별한 LLM API 반복 호출로 인한 무한 로딩 방지)"""
    if not t1 or not t2:
        return 0.0
    clean1 = re.sub(r'[\s\W]+', '', t1.lower())
    clean2 = re.sub(r'[\s\W]+', '', t2.lower())
    if not clean1 or not clean2:
        return 0.0
    return difflib.SequenceMatcher(None, clean1, clean2).ratio()

def fetch_trend_articles(
    keywords: List[str] = None,
    limit_per_keyword: int = 3,
    enable_relevance_filter: bool = True,
    include_domestic: bool = True,
    include_international: bool = True,
    ignore_dedup: bool = False,
    enable_semantic_dedup: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    여러 키워드와 다중 소스에 대해 최신 동향 기사들을 통합 수집 및 2단계 중복 필터링 적용
    
    - 1차 O(1) 정규화 URL & 제목 해시 물리적 중복 제거
    - 2차 LLM 시맨틱 유사도 (80% 이상 중복) 필터링 (로컬 사전필터로 1초 이내 빠른 수집 보장)
    - RSS 차단 시 Fallback Web Scraper 자동 릴레이 전환
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS["ko"]

    all_articles = []
    seen_urls = set()
    seen_titles = set()

    stats = {
        "total_raw": 0,
        "dedup_hash_count": 0,
        "dedup_semantic_count": 0,
        "sources_used": set()
    }

    filter_keywords = []
    if include_domestic:
        filter_keywords.extend(DEFAULT_KEYWORDS["ko"])
    if include_international:
        filter_keywords.extend(DEFAULT_KEYWORDS["en"])

    import llm_router

    # DB 내 최근 수집 기사 대조군 로드 (2차 시맨틱 중복 대조용 - 상위 10건으로 제한)
    recent_db_articles = db_manager.get_recent_articles_for_dedup(limit=10) if enable_semantic_dedup else []

    candidate_articles = []

    # 1. 국내 뉴스 수집
    if include_domestic:
        print(f"🇰🇷 국내 뉴스 수집 시작: {keywords}")
        for kw in keywords:
            google_ko = fetch_google_news_rss(kw, language="ko", max_results=limit_per_keyword, ignore_dedup=ignore_dedup)
            candidate_articles.extend(google_ko)

            naver_ko = fetch_naver_news_search(kw, max_results=limit_per_keyword, ignore_dedup=ignore_dedup)
            candidate_articles.extend(naver_ko)

    # 2. 해외 뉴스 수집
    if include_international:
        international_keywords = list(dict.fromkeys([translate_to_english(kw) for kw in keywords]))
        print(f"🌍 해외 뉴스 수집 시작: {international_keywords}")
        for kw in international_keywords:
            google_en = fetch_google_news_rss(kw, language="en", max_results=limit_per_keyword, ignore_dedup=ignore_dedup)
            candidate_articles.extend(google_en)

    stats["total_raw"] = len(candidate_articles)

    # 3. 1차 O(1) URL 및 제목 해시 중복 제거 & 관련성 필터링
    for art in candidate_articles:
        clean_u = db_manager.normalize_url(art["url"])
        norm_t = db_manager.hash_title(art["title"])

        if not ignore_dedup and (clean_u in seen_urls or norm_t in seen_titles):
            stats["dedup_hash_count"] += 1
            continue

        if enable_relevance_filter:
            is_rel, score = check_article_relevance(art, filter_keywords)
            if not is_rel:
                continue
            art["relevance_score"] = score

        # 4. 2차 LLM 시맨틱 유사도 검증 (80% 이상 의미적 중복 필터링 - Fast Pre-filter 적용)
        if enable_semantic_dedup and not ignore_dedup:
            is_sem_dup = False
            # 대조군을 최근 DB 기사 5건 + 현재 수집된 기사 5건으로 제한
            check_targets = recent_db_articles[:5] + all_articles[-5:]
            for target in check_targets:
                # 로컬 유사도 사전 검사 (유사도 0.3 이상일 때만 AI API 호출)
                local_sim = quick_text_similarity(art["title"], target.get("title", ""))
                if local_sim >= 0.3:
                    try:
                        sem_res = llm_router.check_semantic_duplicate(art, target)
                        if sem_res.get("is_duplicate") or sem_res.get("similarity_score", 0) >= 80:
                            print(f"    🧠 LLM 시맨틱 중복 제외 ({sem_res.get('similarity_score')}%): '{art['title'][:25]}' <-> '{target['title'][:25]}'")
                            is_sem_dup = True
                            stats["dedup_semantic_count"] += 1
                            break
                    except Exception as sem_e:
                        print(f"시맨틱 중복 검사 오류: {sem_e}")
                        break

            if is_sem_dup:
                continue

        seen_urls.add(clean_u)
        seen_titles.add(norm_t)
        stats["sources_used"].add(art.get("source", "RSS"))
        all_articles.append(art)

    if enable_relevance_filter:
        all_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    stats["sources_used"] = list(stats["sources_used"])
    print(f"🎯 최종 {len(all_articles)}건 수집 완료 (RAW: {stats['total_raw']}, Hash 필터: {stats['dedup_hash_count']}, LLM 시맨틱 필터: {stats['dedup_semantic_count']})")

    return all_articles, stats

def extract_full_article_text(url: str) -> str:
    """기사 URL에 접근하여 본문 텍스트 추출 (추출 실패 시 기본 요청 실패 메시지 처리)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.4 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # 본문 태그 추정 (p, article 태그)
            paragraphs = soup.find_all(["p", "article"])
            text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
            if text_blocks:
                return "\n\n".join(text_blocks[:10])
    except Exception as e:
        print(f"Full text extract failed for {url}: {e}")
    return ""
