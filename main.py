# -*- coding: utf-8 -*-
"""
按顺序执行完整流程：
  1. crawl.py      — 抓取并下载数据
  2. merge_data.py — 合并为一览表 Master{YYYYMMDD}.csv
  3. calc_car.py   — 计算综合评估并输出 CAR{YYYYMMDD}.xlsx
  4. plot_car.py   — 根据综合评估表生成欧赔/凯利曲线图

任一步失败则终止，不执行后续步骤。
用法: python main.py [merge_data / calc_car / plot_car 的目录参数...]
  不传参数时使用默认（当天 YYYYMMDD）。
  传参示例: python main.py 20260307
            python main.py 20260306 20260307 20260308
"""
import subprocess
import sys


def main():
    steps = [
        ("crawl.py", ["crawl.py"]),
        ("merge_data.py", ["merge_data.py"] + sys.argv[1:]),
        ("calc_car.py", ["calc_car.py"] + sys.argv[1:]),
        ("plot_car.py", ["plot_car.py"] + sys.argv[1:]),
    ]
    for name, cmd in steps:
        print(f"\n>>> 执行: {' '.join(cmd)}\n")
        ret = subprocess.run([sys.executable] + cmd)
        if ret.returncode != 0:
            print(f"\n>>> {name} 退出码 {ret.returncode}，流程已终止。")
            sys.exit(ret.returncode)
    print("\n>>> 全部步骤执行完成。\n")


if __name__ == "__main__":
    main()
