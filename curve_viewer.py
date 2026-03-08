# -*- coding: utf-8 -*-
"""
曲线图查看服务：根据日期和球队名（主队 VS 客队）搜索并展示生成的曲线图。

本地/开发：python curve_viewer.py  → http://127.0.0.1:5000

生产部署（推荐 Gunicorn）：
  gunicorn -w 4 -b 0.0.0.0:5000 "curve_viewer:app"
  可选：前接 Nginx 做反向代理、HTTPS、限流等。
"""
import os
import re
from urllib.parse import unquote

from flask import Flask, send_from_directory, jsonify, request, send_file

from config import DOWNLOAD_DIR

app = Flask(__name__, static_folder=None)

# 曲线图文件名格式：{主队}_VS_{客队}_曲线.png
CURVE_SUFFIX = "_曲线.png"
VS_SEP = "_VS_"


def _parse_curve_filename(basename: str):
    """从文件名解析出 (主队, 客队)，若不是曲线图返回 None。"""
    if not basename.endswith(CURVE_SUFFIX):
        return None
    name = basename[: -len(CURVE_SUFFIX)]
    if VS_SEP not in name:
        return None
    parts = name.split(VS_SEP, 1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else None


def _match_team(keyword: str, home: str, away: str) -> bool:
    """球队名关键词是否匹配主队或客队（含即算匹配）。"""
    if not keyword or not keyword.strip():
        return True
    k = keyword.strip()
    return k in home or k in away


@app.route("/")
def index():
    """返回搜索页面。"""
    return send_file(
        os.path.join(os.path.dirname(__file__), "curve_viewer.html"),
        mimetype="text/html",
    )


@app.route("/api/dates")
def api_dates():
    """列出 DOWNLOAD_DIR 下所有日期目录（YYYYMMDD）。"""
    if not os.path.isdir(DOWNLOAD_DIR):
        return jsonify({"dates": []})
    dirs = []
    for name in os.listdir(DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, name)
        if os.path.isdir(path) and re.match(r"^\d{8}$", name):
            dirs.append(name)
    dirs.sort(reverse=True)
    return jsonify({"dates": dirs})


@app.route("/api/search")
def api_search():
    """按日期和球队名搜索曲线图。参数: date=YYYYMMDD, team=可选关键词。"""
    date = (request.args.get("date") or "").strip()
    team = (request.args.get("team") or "").strip()
    if not date or not re.match(r"^\d{8}$", date):
        return jsonify({"error": "请提供有效日期 YYYYMMDD", "items": []})
    dir_path = os.path.join(DOWNLOAD_DIR, date)
    if not os.path.isdir(dir_path):
        return jsonify({"date": date, "items": []})
    items = []
    for fn in os.listdir(dir_path):
        if not fn.endswith(CURVE_SUFFIX):
            continue
        parsed = _parse_curve_filename(fn)
        if not parsed:
            continue
        home, away = parsed
        if not _match_team(team, home, away):
            continue
        items.append({
            "date": date,
            "home": home,
            "away": away,
            "filename": fn,
        })
    items.sort(key=lambda x: (x["home"], x["away"]))
    return jsonify({"date": date, "items": items})


@app.route("/img/<date>/<path:filename>")
def serve_image(date, filename):
    """按日期和文件名提供曲线图图片。"""
    if not re.match(r"^\d{8}$", date):
        return "", 404
    dir_path = os.path.join(DOWNLOAD_DIR, date)
    filename = unquote(filename)
    if ".." in filename or not filename.endswith(CURVE_SUFFIX):
        return "", 404
    path = os.path.join(dir_path, filename)
    if not os.path.isfile(path):
        return "", 404
    return send_from_directory(dir_path, filename, mimetype="image/png")


def main():
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
