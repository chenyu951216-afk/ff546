from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests

from app.core.config import NEWS_API_KEY, USE_SAMPLE_DATA

KEYWORD_BUCKETS = {
    'AI伺服器': ['ai', 'server', 'gb200', '資料中心', '伺服器'],
    '半導體': ['半導體', '晶片', 'foundry', '晶圓', 'chip'],
    '重電': ['重電', '電網', '變壓器', '台電'],
    '散熱': ['散熱', 'cooling', '熱模組'],
    '航運': ['航運', '貨櫃', '運價'],
}

POSITIVE_WORDS = ['受惠', '成長', '上修', '擴產', '利多', '強勢', '突破', '訂單']
NEGATIVE_WORDS = ['風險', '下修', '衰退', '利空', '跌破', '疲弱', '壓力', '關稅']


def _sample_news() -> List[Dict[str, Any]]:
    return [
        {'title': 'AI 伺服器供應鏈持續受惠，市場聚焦出貨動能', 'summary': '市場預期 AI 伺服器出貨延續，散熱與電源供應鏈同步受惠。', 'sector': 'AI伺服器', 'sentiment': 'positive', 'source': 'sample'},
        {'title': '台電強韌電網政策延伸，重電族群關注度升高', 'summary': '重電與電力設備相關個股再度受到資金注意。', 'sector': '重電', 'sentiment': 'positive', 'source': 'sample'},
        {'title': '市場觀望國際利率與關稅變數，短線波動擴大', 'summary': '高估值科技股短線震盪風險提升。', 'sector': '市場', 'sentiment': 'neutral', 'source': 'sample'},
    ]


def classify_sector(text: str) -> str:
    lower_text = text.lower()
    for sector, keywords in KEYWORD_BUCKETS.items():
        if any(keyword.lower() in lower_text for keyword in keywords):
            return sector
    return '市場'


def classify_sentiment(text: str) -> str:
    lower_text = text.lower()
    if any(word in lower_text for word in POSITIVE_WORDS):
        return 'positive'
    if any(word in lower_text for word in NEGATIVE_WORDS):
        return 'negative'
    return 'neutral'


def fetch_news() -> List[Dict[str, Any]]:
    if USE_SAMPLE_DATA or not NEWS_API_KEY:
        return _sample_news()

    params = {
        'q': '(Taiwan stock OR 台股 OR 上市 OR 上櫃) AND (AI OR 半導體 OR 重電 OR 散熱 OR 航運)',
        'language': 'zh',
        'sortBy': 'publishedAt',
        'from': (datetime.now(timezone.utc) - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'pageSize': 30,
        'apiKey': NEWS_API_KEY,
    }
    try:
        response = requests.get('https://newsapi.org/v2/everything', params=params, timeout=20)
        response.raise_for_status()
        articles = response.json().get('articles', [])
    except Exception:
        return _sample_news()

    rows: List[Dict[str, Any]] = []
    for article in articles:
        title = article.get('title') or ''
        summary = article.get('description') or article.get('content') or ''
        joined = f'{title} {summary}'
        rows.append({
            'title': title,
            'summary': summary,
            'sector': classify_sector(joined),
            'sentiment': classify_sentiment(joined),
            'source': article.get('source', {}).get('name', 'newsapi'),
            'published_at': article.get('publishedAt', ''),
        })
    return rows or _sample_news()


def build_news_snapshot() -> Dict[str, Any]:
    news = fetch_news()
    sector_counts = defaultdict(int)
    sector_scores = defaultdict(int)
    for item in news:
        sector = item['sector']
        sector_counts[sector] += 1
        sector_scores[sector] += 1 if item['sentiment'] == 'positive' else -1 if item['sentiment'] == 'negative' else 0

    hot_sectors = sorted(
        [{'sector': sector, 'count': count, 'score': sector_scores[sector]} for sector, count in sector_counts.items()],
        key=lambda x: (x['score'], x['count']),
        reverse=True,
    )
    return {
        'news': news,
        'hot_sectors': hot_sectors,
        'market_bias': '偏多' if sum(1 for n in news if n['sentiment'] == 'positive') >= sum(1 for n in news if n['sentiment'] == 'negative') else '偏保守',
    }
