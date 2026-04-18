from __future__ import annotations

from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import MONITOR_INTERVAL_MINUTES
from app.services.ranking_service import build_rankings
from app.services.alerts_service import get_alerts
from app.services.openai_service import analyze_monthly_report


def morning_ranking_job() -> None:
    build_rankings()


def intraday_monitor_job() -> None:
    get_alerts()


def monthly_ai_job() -> None:
    analyze_monthly_report([{'stock_id': 'sample', 'industry': '市場', 'score': 80}])


def build_scheduler() -> Optional[BackgroundScheduler]:
    scheduler = BackgroundScheduler(timezone='Asia/Taipei')
    scheduler.add_job(morning_ranking_job, 'cron', hour=8, minute=50, id='morning_ranking')
    scheduler.add_job(intraday_monitor_job, 'interval', minutes=MONITOR_INTERVAL_MINUTES, id='intraday_monitor')
    scheduler.add_job(monthly_ai_job, 'cron', day=1, hour=7, minute=30, id='monthly_ai_report')
    return scheduler
