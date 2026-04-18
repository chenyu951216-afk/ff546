import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'development')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5.4-mini')
OPENAI_MONTHLY_BUDGET_TWD = float(os.getenv('OPENAI_MONTHLY_BUDGET_TWD', '500'))
FX_USD_TWD = float(os.getenv('FX_USD_TWD', '32.5'))
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
TWSE_BASE_URL = os.getenv('TWSE_BASE_URL', 'https://openapi.twse.com.tw/v1')
MONITOR_INTERVAL_MINUTES = int(os.getenv('MONITOR_INTERVAL_MINUTES', '15'))
USE_SAMPLE_DATA = os.getenv('USE_SAMPLE_DATA', 'true').lower() == 'true'
