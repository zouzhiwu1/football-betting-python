"""
爬虫配置。可通过环境变量覆盖（若存在 .env 会先加载）：
  CRAWLER_BASE_URL  页面地址
  CRAWLER_DOWNLOAD_DIR  下载目录
  CRAWLER_CUTOFF_HOUR  跨天时间临界点（时，0～23），默认 12
  CRAWLER_TIMEZONE  用于“当前时间”的时区（决定下载目录/文件名），默认 Asia/Shanghai
  CRAWLER_HEADLESS  设为 1 则无头模式
  CRAWLER_DEBUG_LOG_DIR  日志目录（定时任务日志、debug_export_page_*.html 等），默认 football-betting-log
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = os.environ.get(
    "CRAWLER_BASE_URL",
    "https://live.nowscore.com/2in1.aspx"
)
DOWNLOAD_DIR = os.environ.get(
    "CRAWLER_DOWNLOAD_DIR",
    "/Users/zhiwuzou/Documents/cursor/football-betting-data"
)
# 跨天时间临界点（时）：当日该时及之后 → 当日文件夹；次日该时之前 → 前一日文件夹
CUTOFF_HOUR = int(os.environ.get("CRAWLER_CUTOFF_HOUR", "12"))
# 用于“当前时间”的时区（避免服务器 UTC 导致临界点错位）
TIMEZONE = os.environ.get("CRAWLER_TIMEZONE", "Asia/Shanghai")
HEADLESS = os.environ.get("CRAWLER_HEADLESS", "1") == "1"
# 日志目录：定时任务 stdout/stderr、调试导出的页面 HTML（debug_export_page_*.html）等
DEBUG_LOG_DIR = os.environ.get(
    "CRAWLER_DEBUG_LOG_DIR",
    "/Users/zhiwuzou/Documents/cursor/football-betting-log"
)

# 足彩子菜单：目前只抓取「北单」
ZUCAI_MENU_OPTIONS = ["北单"]

# 表格列索引（与页面一致）：选、日期、时间、状态、主队、比分、客队、…
COL_DATE = 1
COL_TIME = 2
COL_HOME = 4
COL_AWAY = 6

# 等待时间（秒）
WAIT_ELEMENT = 20
WAIT_AFTER_CLICK = 0.5
WAIT_AFTER_HOVER = 0.4
WAIT_TABLE_REFRESH = 3
WAIT_ROW_COUNT = 20
WAIT_FIRST_ROW_CHANGED = 12
