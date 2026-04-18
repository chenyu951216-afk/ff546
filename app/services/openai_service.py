from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import FX_USD_TWD, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MONTHLY_BUDGET_TWD

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
USAGE_FILE = DATA_DIR / 'openai_usage.json'

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


MODEL_PRICING_USD_PER_1M = {
    'gpt-5.4': {'input': 2.50, 'output': 15.00},
    'gpt-5.4-mini': {'input': 0.75, 'output': 4.50},
    'gpt-5.4-nano': {'input': 0.15, 'output': 0.60},
}


def _month_key() -> str:
    return datetime.now().strftime('%Y-%m')


def _load_usage() -> Dict[str, Any]:
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def _save_usage(data: Dict[str, Any]) -> None:
    USAGE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _estimate_twd_cost(input_chars: int, output_chars: int) -> float:
    pricing = MODEL_PRICING_USD_PER_1M.get(OPENAI_MODEL, MODEL_PRICING_USD_PER_1M['gpt-5.4-mini'])
    input_tokens = max(input_chars / 4, 1)
    output_tokens = max(output_chars / 4, 1)
    usd = (input_tokens / 1_000_000) * pricing['input'] + (output_tokens / 1_000_000) * pricing['output']
    return round(usd * FX_USD_TWD, 4)


def _can_spend(extra_cost_twd: float) -> bool:
    usage = _load_usage()
    spent = float(usage.get(_month_key(), {}).get('spent_twd', 0))
    return spent + extra_cost_twd <= OPENAI_MONTHLY_BUDGET_TWD


def _record_usage(cost_twd: float, kind: str) -> None:
    usage = _load_usage()
    bucket = usage.setdefault(_month_key(), {'spent_twd': 0, 'calls': []})
    bucket['spent_twd'] = round(float(bucket.get('spent_twd', 0)) + cost_twd, 4)
    bucket['calls'].append({'ts': datetime.now().isoformat(timespec='seconds'), 'kind': kind, 'cost_twd': cost_twd})
    _save_usage(usage)


def get_usage_snapshot() -> Dict[str, Any]:
    usage = _load_usage().get(_month_key(), {'spent_twd': 0, 'calls': []})
    return {
        'month': _month_key(),
        'budget_twd': OPENAI_MONTHLY_BUDGET_TWD,
        'spent_twd': round(float(usage.get('spent_twd', 0)), 4),
        'remaining_twd': round(OPENAI_MONTHLY_BUDGET_TWD - float(usage.get('spent_twd', 0)), 4),
        'calls_this_month': len(usage.get('calls', [])),
        'model': OPENAI_MODEL,
    }


def _fallback_market_analysis(candidate_rows: List[Dict[str, Any]], hot_sectors: List[Dict[str, Any]]) -> Dict[str, Any]:
    sector_text = '、'.join([x['sector'] for x in hot_sectors[:3]]) or '市場輪動'
    comments = []
    for row in candidate_rows[:5]:
        comments.append({
            'stock_id': row['stock_id'],
            'bias': 'positive' if row.get('sector_score', 0) >= 0 else 'neutral',
            'summary': f"{row['stock_name']} 受 {row['industry']} 題材支撐，適合 3-10 天波段觀察。",
            'risk': '若量能縮減或跌破短線結構，需提高警戒。',
            'holding_days': row.get('holding_days', 5),
            'confidence': 0.62,
        })
    return {
        'market_theme': f'主線聚焦 {sector_text}',
        'risk_summary': '新聞只作加分，排名仍以量價、結構、產業強度為主。',
        'stock_comments': comments,
        'source': 'fallback',
    }


def analyze_market(candidate_rows: List[Dict[str, Any]], hot_sectors: List[Dict[str, Any]], top_news: List[Dict[str, Any]]) -> Dict[str, Any]:
    prompt_payload = {
        'task': '請用繁體中文，分析台股未來 3-10 天波段機會。新聞只作加分項，不要讓新聞主導結論。輸出 JSON。',
        'hot_sectors': hot_sectors[:8],
        'candidate_rows': candidate_rows[:12],
        'top_news': top_news[:12],
    }
    estimated_cost = _estimate_twd_cost(len(json.dumps(prompt_payload, ensure_ascii=False)), 1200)
    if not OPENAI_API_KEY or not OpenAI or not _can_spend(estimated_cost):
        return _fallback_market_analysis(candidate_rows, hot_sectors)

    schema = {
        'name': 'market_analysis',
        'schema': {
            'type': 'object',
            'properties': {
                'market_theme': {'type': 'string'},
                'risk_summary': {'type': 'string'},
                'stock_comments': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'stock_id': {'type': 'string'},
                            'bias': {'type': 'string'},
                            'summary': {'type': 'string'},
                            'risk': {'type': 'string'},
                            'holding_days': {'type': 'integer'},
                            'confidence': {'type': 'number'},
                        },
                        'required': ['stock_id', 'bias', 'summary', 'risk', 'holding_days', 'confidence'],
                        'additionalProperties': False,
                    },
                },
            },
            'required': ['market_theme', 'risk_summary', 'stock_comments'],
            'additionalProperties': False,
        },
    }

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[{'role': 'user', 'content': [{'type': 'input_text', 'text': json.dumps(prompt_payload, ensure_ascii=False)}]}],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': schema['name'],
                    'schema': schema['schema'],
                    'strict': True,
                }
            },
        )
        parsed = json.loads(response.output_text)
        _record_usage(estimated_cost, 'daily_market_analysis')
        parsed['source'] = 'openai'
        return parsed
    except Exception:
        return _fallback_market_analysis(candidate_rows, hot_sectors)


def analyze_monthly_report(monthly_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    prompt_payload = {
        'task': '根據最近一個月台股候選股與警示資料，總結哪些產業、型態、風險最常出現。請輸出 JSON。',
        'monthly_rows': monthly_rows[:120],
    }
    estimated_cost = _estimate_twd_cost(len(json.dumps(prompt_payload, ensure_ascii=False)), 1800)
    if not OPENAI_API_KEY or not OpenAI or not _can_spend(estimated_cost):
        return {
            'summary': '本月 AI 預算未啟用或已達上限，改用本地月報。熱門題材仍以 AI 伺服器、半導體、重電為主。',
            'best_patterns': ['放量轉強', '產業共振', '分數穩定上升'],
            'risk_patterns': ['高檔爆量', '跌破短線結構', '題材退潮'],
            'source': 'fallback',
        }
    schema = {
        'name': 'monthly_report',
        'schema': {
            'type': 'object',
            'properties': {
                'summary': {'type': 'string'},
                'best_patterns': {'type': 'array', 'items': {'type': 'string'}},
                'risk_patterns': {'type': 'array', 'items': {'type': 'string'}},
            },
            'required': ['summary', 'best_patterns', 'risk_patterns'],
            'additionalProperties': False,
        },
    }
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[{'role': 'user', 'content': [{'type': 'input_text', 'text': json.dumps(prompt_payload, ensure_ascii=False)}]}],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': schema['name'],
                    'schema': schema['schema'],
                    'strict': True,
                }
            },
        )
        parsed = json.loads(response.output_text)
        _record_usage(estimated_cost, 'monthly_report')
        parsed['source'] = 'openai'
        return parsed
    except Exception:
        return {
            'summary': '月報分析失敗，改用本地摘要。',
            'best_patterns': ['產業主流延續', '回檔不破均線'],
            'risk_patterns': ['利多不漲', '高檔爆量'],
            'source': 'fallback',
        }
