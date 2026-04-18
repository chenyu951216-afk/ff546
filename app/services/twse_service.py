from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import random
import requests

from app.core.config import TWSE_BASE_URL, USE_SAMPLE_DATA


@dataclass
class StockQuote:
    stock_id: str
    stock_name: str
    industry: str
    close: float
    pct_change: float
    volume: int
    turnover_million: float
    is_limit_up: bool
    is_limit_down: bool


def _sample_quotes() -> List[StockQuote]:
    sample = [
        ('2330', '台積電', '半導體'),
        ('2382', '廣達', 'AI伺服器'),
        ('3231', '緯創', 'AI伺服器'),
        ('6669', '緯穎', 'AI伺服器'),
        ('1519', '華城', '重電'),
        ('3017', '奇鋐', '散熱'),
        ('3324', '雙鴻', '散熱'),
        ('2308', '台達電', '電源供應'),
        ('2317', '鴻海', '電子代工'),
        ('2603', '長榮', '航運'),
        ('3443', '創意', 'IC設計'),
        ('3661', '世芯-KY', 'IC設計'),
    ]
    quotes: List[StockQuote] = []
    for sid, name, industry in sample:
        close = round(random.uniform(80, 1200), 2)
        pct = round(random.uniform(-3.0, 8.8), 2)
        volume = random.randint(3000, 120000)
        turnover = round(close * volume / 1000, 2)
        quotes.append(
            StockQuote(
                stock_id=sid,
                stock_name=name,
                industry=industry,
                close=close,
                pct_change=pct,
                volume=volume,
                turnover_million=turnover,
                is_limit_up=pct >= 9.0,
                is_limit_down=pct <= -9.0,
            )
        )
    return quotes


def _normalize_latest(payload: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not isinstance(payload, list):
        return rows
    for item in payload:
        stock_id = str(item.get('Code') or item.get('股票代號') or '')
        if not stock_id.isdigit():
            continue
        try:
            close = float(str(item.get('ClosingPrice') or item.get('收盤價') or item.get('AvgClosingPrice') or 0).replace(',', ''))
        except Exception:
            close = 0.0
        try:
            volume = int(float(str(item.get('TradeVolume') or item.get('成交股數') or 0).replace(',', '')))
        except Exception:
            volume = 0
        rows.append(
            {
                'stock_id': stock_id,
                'stock_name': item.get('Name') or item.get('股票名稱') or stock_id,
                'industry': item.get('Industry') or item.get('產業別') or '未分類',
                'close': close,
                'pct_change': 0.0,
                'volume': volume,
                'turnover_million': round(close * volume / 1000, 2) if close and volume else 0.0,
                'is_limit_up': False,
                'is_limit_down': False,
            }
        )
    return rows


def fetch_market_quotes() -> List[Dict[str, Any]]:
    if USE_SAMPLE_DATA:
        return [q.__dict__ for q in _sample_quotes()]

    endpoints = [
        '/exchangeReport/STOCK_DAY_ALL',
        '/exchangeReport/STOCK_DAY_AVG_ALL',
    ]
    for endpoint in endpoints:
        try:
            response = requests.get(f'{TWSE_BASE_URL}{endpoint}', timeout=20)
            response.raise_for_status()
            rows = _normalize_latest(response.json())
            if rows:
                return rows[:500]
        except Exception:
            continue
    return [q.__dict__ for q in _sample_quotes()]
