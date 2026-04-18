from __future__ import annotations

from typing import Dict, List

from app.services.watchlist_service import get_watchlist


def get_alerts() -> List[Dict]:
    alerts: List[Dict] = []
    for item in get_watchlist():
        if item['status'] == '正常':
            continue
        alerts.append({
            'stock_id': item['stock_id'],
            'stock_name': item['stock_name'],
            'level': item['status'],
            'reason': f"分數下降 {item['score_drop']}，當日漲跌 {item['pct_change']}%，原 thesis：{item['thesis']}",
        })
    return alerts
