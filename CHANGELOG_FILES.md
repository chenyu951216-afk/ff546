# 本次更新改動檔案 v0.3

## 新增 / 重做
- app/core/config.py
- app/services/news_service.py
- app/services/twse_service.py
- app/services/openai_service.py
- app/services/ranking_service.py
- app/services/watchlist_service.py
- app/services/alerts_service.py
- app/tasks/scheduler.py
- app/templates/base.html
- app/templates/dashboard.html
- app/templates/ranking.html
- app/templates/watchlist.html
- app/templates/alerts.html
- app/static/style.css
- .env
- .env.example
- README.md

## 主要改動
1. 新聞改成只做加分與風險補充，不再主導排名。
2. 排名改以量價、結構、流動性、產業主流為主，較接近 3-10 天波段。
3. TWSE 抓取上限改成 500 檔。
4. OpenAI 改用 `gpt-5.4-mini` 預設，新增每月 TWD 500 預算控管。
5. 增加每月 AI 月報與使用量統計。
6. 盤中監控與警示文案加上 thesis 說明。
