from __future__ import annotations

from typing import Any, Dict, List

from app.services.news_service import build_news_snapshot
from app.services.openai_service import analyze_market, analyze_monthly_report, get_usage_snapshot
from app.services.risk_service import calculate_risk
from app.services.twse_service import fetch_market_quotes
from app.services.alerts_service import get_alerts


def _sector_strength_map(hot_sectors: List[Dict[str, Any]]) -> Dict[str, int]:
    return {item['sector']: item['score'] * 3 + item['count'] * 2 for item in hot_sectors}


def _score_row(row: Dict[str, Any], sector_strength: Dict[str, int]) -> Dict[str, Any]:
    pct = row['pct_change']
    vol_score = min(row['volume'] / 20000, 5) * 4
    price_action_score = 22 + max(min(pct, 9), -5) * 3
    liquidity_score = min(row['turnover_million'] / 20000, 6) * 3
    sector_score = sector_strength.get(row['industry'], sector_strength.get('市場', 0))
    trend_score = 16 if pct > 3 else 10 if pct > 0 else 4
    risk_penalty = 8 if pct < -2 else 0
    total_score = round(price_action_score + vol_score + liquidity_score + sector_score + trend_score - risk_penalty, 2)
    return {
        **row,
        'sector_score': sector_score,
        'price_action_score': round(price_action_score, 2),
        'volume_score': round(vol_score, 2),
        'liquidity_score': round(liquidity_score, 2),
        'trend_score': trend_score,
        'news_score': max(sector_score, 0),
        'total_score': total_score,
    }


def build_rankings() -> Dict[str, Any]:
    quotes = fetch_market_quotes()[:500]
    news_snapshot = build_news_snapshot()
    sector_strength = _sector_strength_map(news_snapshot['hot_sectors'])
    scored = [_score_row(row, sector_strength) for row in quotes]
    scored.sort(key=lambda x: x['total_score'], reverse=True)
    top_candidates = scored[:12]

    ai_result = analyze_market(top_candidates, news_snapshot['hot_sectors'], news_snapshot['news'])
    ai_map = {item['stock_id']: item for item in ai_result['stock_comments']}

    all_rankings: List[Dict[str, Any]] = []
    for row in scored:
        risk = calculate_risk(row['close'], row['total_score'])
        ai_row = ai_map.get(row['stock_id'], {})
        ai_bonus = 4 if ai_row.get('bias') == 'positive' else 1 if ai_row.get('bias') == 'neutral' else -2
        final_score = round(row['total_score'] + ai_bonus, 2)
        all_rankings.append({
            **row,
            **risk,
            'total_score': final_score,
            'ai_bias': ai_row.get('bias', 'neutral'),
            'ai_summary': ai_row.get('summary', '本檔未進入 AI 前段評論，維持系統評分。'),
            'ai_risk': ai_row.get('risk', '注意量縮與跌破結構風險。'),
            'ai_confidence': ai_row.get('confidence', 0.5),
        })

    all_rankings.sort(key=lambda x: x['total_score'], reverse=True)
    rankings = all_rankings[:5]

    monthly_rows = [{'stock_id': r['stock_id'], 'industry': r['industry'], 'score': r['total_score']} for r in all_rankings[:40]] + get_alerts()
    monthly_report = analyze_monthly_report(monthly_rows)

    return {
        'rankings': rankings,
        'all_rankings': all_rankings[:60],
        'market_theme': ai_result['market_theme'],
        'risk_summary': ai_result['risk_summary'],
        'hot_sectors': news_snapshot['hot_sectors'][:6],
        'usage_snapshot': get_usage_snapshot(),
        'monthly_report': monthly_report,
    }
