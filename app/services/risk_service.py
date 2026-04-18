from typing import Dict


def calculate_risk(price: float, score: float) -> Dict[str, float]:
    atr_like = max(price * 0.028, 1.0)
    structural_buffer = price * 0.018
    stop_loss = round(max(price - atr_like - structural_buffer, 0.01), 2)
    r = max(price - stop_loss, 0.01)
    hold_days = 6 if score >= 86 else 5 if score >= 78 else 4
    return {
        'stop_loss': stop_loss,
        'tp1': round(price + r * 1.2, 2),
        'tp2': round(price + r * 2.0, 2),
        'tp3': round(price + r * 3.0, 2),
        'holding_days': hold_days,
    }


def alert_level(score_drop: float, pct_change: float) -> str:
    if score_drop >= 12 or pct_change <= -5:
        return '紅燈'
    if score_drop >= 7 or pct_change <= -3:
        return '橘燈'
    if score_drop >= 4 or pct_change <= -1.5:
        return '黃燈'
    return '正常'
