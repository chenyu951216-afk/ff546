# TW Stock Insight Bot v0.3

## 啟動
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 功能
- TWSE OpenAPI 接入骨架（最多抓 500 檔）
- News API 接入骨架與產業/情緒分類
- OpenAI Responses API 結構化分析
- OpenAI 月度預算上限控制（預設 TWD 500）
- 每日 Top 5 候選股
- 持股追蹤與盤中警示
- 止損 / 止盈 / 建議持有天數
- 每月 AI 月報

## 設定
1. `.env` 填入 `OPENAI_API_KEY`、`NEWS_API_KEY`
2. 想先看畫面可維持 `USE_SAMPLE_DATA=true`
3. 要切真資料，改成 `USE_SAMPLE_DATA=false`

## 設計原則
- 新聞只是加分，不主導排名。
- 排名以量價、結構、流動性、產業主流為主。
- OpenAI 只做摘要、風險補充、月報與小幅加權。
