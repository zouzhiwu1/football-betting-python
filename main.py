# -*- coding: utf-8 -*-
"""
按顺序执行完整流程：
  1. crawl.py      — 抓取并下载数据
  2. merge_data.py — 合并为一览表 Master{YYYYMMDD}.csv
  3. calc_car.py   — 计算综合评估并输出 CAR{YYYYMMDD}.xlsx
  4. plot_car.py   — 根据综合评估表生成欧赔/凯利曲线图

任一步失败则终止，不执行后续步骤。

日志：
- 详细流程日志写入 DEBUG_LOG_DIR/main_{YYYYMMDDHH}.log（按小时分文件，带日期时间）。
- 若通过 launchd 等重定向 stdout/stderr，则仍可在系统指定的 log/err 文件中看到部分输出。

用法: python main.py
  - 无参数：按当前时间自动计算本次统计区间 [start,end]（基于固定触发时刻），
    然后依次执行 crawl.py、merge_data.py start end、calc_car.py {start日期}、plot_car.py {start日期}。
"""
import logging
import os
from datetime import datetime, timedelta
import subprocess
import sys

from config import DEBUG_LOG_DIR, LOG_RETENTION_DAYS
from log_cleanup import delete_old_logs


def _setup_logging():
    """配置主流程日志到 main_{YYYYMMDDHH}.log，并输出到终端。"""
    os.makedirs(DEBUG_LOG_DIR, exist_ok=True)
    time_suffix = datetime.now().strftime("%Y%m%d%H")
    log_path = os.path.join(DEBUG_LOG_DIR, f"main_{time_suffix}.log")
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info("主流程日志文件: %s", log_path)
    return logger


def _compute_time_window(now: datetime):
    """
    根据当前时间计算本次统计区间 [start_dt, end_dt]（闭区间，按小时）。

    固定触发时刻为：2,4,6,15,17,19,21,23 点。

    规则：
    - 若当前小时正好是触发时刻之一（定时任务按点执行）：
        end = 当前小时，对应触发时刻；
        start = 上一个触发时刻（可能在同一天或前一天）。
    - 若当前小时不是触发时刻（你手工在任意时间执行 main.py）：
        end = 当前小时（向下取整，不含分钟）；
        start = 最近一个 <= 当前小时的触发时刻；若当天还没到任何触发时刻，则取“前一天的 23 点”。
    """
    TRIGGER_HOURS = [2, 4, 6, 15, 17, 19, 21, 23]
    TRIGGER_HOURS.sort()

    now_hour = now.hour

    # 情况一：当前小时正好是触发时刻（定时执行）
    if now_hour in TRIGGER_HOURS:
        end_hour = now_hour
        end_date = now.date()
        idx = TRIGGER_HOURS.index(end_hour)
        if idx > 0:
            start_hour = TRIGGER_HOURS[idx - 1]
            start_date = end_date
        else:
            start_hour = TRIGGER_HOURS[-1]
            start_date = end_date - timedelta(days=1)
    else:
        # 情况二：手工在任意时间执行，end 用当前小时，start 用最近一个 <= 当前小时的触发时刻
        end_hour = now_hour
        end_date = now.date()
        candidates = [h for h in TRIGGER_HOURS if h <= now_hour]
        if candidates:
            start_hour = max(candidates)
            start_date = end_date
        else:
            # 当前时间在当天第一触发时刻之前：回退到前一天 23 点
            start_hour = TRIGGER_HOURS[-1]
            start_date = (now - timedelta(days=1)).date()

    start_dt = datetime(start_date.year, start_date.month, start_date.day, start_hour)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, end_hour)
    return start_dt, end_dt


def main():
    log = _setup_logging()
    removed = delete_old_logs(DEBUG_LOG_DIR, days=LOG_RETENTION_DAYS)
    if removed:
        log.info(
            "已删除 %d 个超过 %d 天的日志文件: %s",
            len(removed),
            LOG_RETENTION_DAYS,
            removed,
        )

    # 计算本次统计区间 [start,end]，并生成传给各脚本的参数
    now = datetime.now()
    start_dt, end_dt = _compute_time_window(now)
    start_arg = start_dt.strftime("%Y%m%d%H")
    end_arg = end_dt.strftime("%Y%m%d%H")
    logical_date = start_dt.strftime("%Y%m%d")  # 与 merge_data.py 的输出日期一致

    log.info(
        "本次统计区间: [%s, %s]，逻辑日期=%s",
        start_arg,
        end_arg,
        logical_date,
    )

    steps = [
        ("crawl.py", ["crawl.py"]),
        ("merge_data.py", ["merge_data.py", start_arg, end_arg]),
        ("calc_car.py", ["calc_car.py", logical_date]),
        ("plot_car.py", ["plot_car.py", logical_date]),
    ]
    for name, cmd in steps:
        log.info(">>> 执行: %s", " ".join(cmd))
        ret = subprocess.run([sys.executable] + cmd)
        if ret.returncode != 0:
            log.error(">>> %s 退出码 %d，流程已终止。", name, ret.returncode)
            sys.exit(ret.returncode)
    log.info(">>> 全部步骤执行完成。")


if __name__ == "__main__":
    main()
