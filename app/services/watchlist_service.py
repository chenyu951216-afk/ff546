from __future__ import annotations

from typing import Dict, List

from app.services.risk_service import alert_level

WATCHLIST: List[Dict] = [
    {'stock_id': '2382', 'stock_name': '廣達', 'entry_price': 280.0, 'current_score': 86, 'prev_score': 92, 'pct_change': -2.4, 'thesis': 'AI伺服器主流延續'},
    {'stock_id': '1519', 'stock_name': '華城', 'entry_price': 650.0, 'current_score': 79, 'prev_score': 82, 'pct_change': 1.2, 'thesis': '重電題材與政策支撐'},
]


def get_watchlist() -> List[Dict]:
    rows = []
    for item in WATCHLIST:
        drop = item['prev_score'] - item['current_score']
        rows.append({
            **item,
            'score_drop': drop,
            'status': alert_level(drop, item['pct_change']),
        })
    return rows
