# 足球比分爬虫（Python 版）

打开智云比分页，点击「足球」→「足彩」下的 竞足/北单/14场，等待表格刷新后抓取并下载数据；可配合 merge_data、calc_car、plot_car 完成合并、计算与曲线图生成流程。

## 环境

- Python 3.10+
- Chrome 浏览器

## 安装

```bash
cd football-betting-python
pip install -r requirements.txt
```

## 运行

一键执行完整流程（抓取 → 合并 → 计算 → 曲线图）：

```bash
python main.py
```

也可单独执行各步骤，见下文「脚本说明」。

## 脚本说明

### crawl.py — 抓取数据

**功能**：打开智云比分页，进入「足球」→「足彩」下的北单等入口，等待表格刷新后，逐场点击导出并下载对应的 `.xls` 文件。文件按配置的下载目录与跨天临界点保存到子目录 `{YYYYMMDD}/`，文件名含主客队与时间点（如 `主队 VS 客队2026030807.xls`）。

**用法**：

```bash
python crawl.py
```

无参数，依赖 `config.py` / 环境变量中的 `CRAWLER_DOWNLOAD_DIR`、`CRAWLER_CUTOFF_HOUR`、`CRAWLER_TIMEZONE` 等。

---

### merge_data.py — 合并一览表

**功能**：将指定日期目录下的所有 `.xls` 数据文件按文件名排序后合并为一张一览表，输出 `Master{YYYYMMDD}.csv`。表头两行来自工程目录下的 `template.xlsx` 第 1、2 行；数据列为 C/D/E/F/G/H/L/M/N 等。

**用法**：

```bash
python merge_data.py                    # 处理当天日期目录（基于 DOWNLOAD_DIR）
python merge_data.py 20260307           # 处理 20260307 目录（相对路径基于 DOWNLOAD_DIR）
python merge_data.py /path/to/20260307  # 绝对路径
```

- 不传参数时默认为当天 `YYYYMMDD`。
- 目录可为相对路径（相对于 `config.DOWNLOAD_DIR`）或绝对路径。
- 工程目录下需有 `template.xlsx`。

---

### calc_car.py — 计算综合评估（CAR）

**功能**：在 merge_data 生成的一览表基础上，按「主队、客队、时间点」分组，对 D～L 列计算综合评估值：D～I 列用 `(MAX-MIN)/AVERAGE`，J、K、L 列用 `VARP(列)*100`，输出 `CAR{YYYYMMDD}.xlsx`。

**用法**：

```bash
python calc_car.py                      # 处理当天目录
python calc_car.py 20260307             # 处理 20260307
python calc_car.py 20260306 20260307 20260308   # 处理多个目录
```

- 不传参数时默认为当天 `YYYYMMDD`。
- 可传多个目录（相对路径基于 `DOWNLOAD_DIR` 或绝对路径）。
- 依赖：同一目录下需已存在 `Master{YYYYMMDD}.csv`（即先运行 merge_data.py）；工程目录下需有 `template.xlsx`。

---

### plot_car.py — 生成欧赔/凯利曲线图

**功能**：根据综合评估表 `CAR{YYYYMMDD}.xlsx` 为每场比赛生成一张图，包含两个子图：**欧赔指数曲线图**（主/平/客三条曲线，第 1 节点为初指 D/E/F，其余节点为各时间点即时盘 G/H/I）、**凯利指数曲线图**（主/平/客三条曲线，X 轴为时间点 C，Y 轴为 J/K/L）。曲线节点数量由表中该场比赛的时间点数量决定，不固定。详见 design.md 第 3.3 节。

**用法**：

```bash
python plot_car.py                      # 处理当天目录
python plot_car.py 20260307              # 处理 20260307
python plot_car.py 20260306 20260307     # 处理多个目录
```

- 参数与 merge_data.py 一致：不传参数时默认为当天 `YYYYMMDD`；可传多个目录（相对路径基于 DOWNLOAD_DIR）。
- 输出图片保存在对应数据目录下，文件名：`{主队}_VS_{客队}_曲线.png`。
- 依赖：同一目录下需已存在 `CAR{YYYYMMDD}.xlsx`（即先运行 calc_car.py）。

---

## 配置

所有配置均可通过**环境变量**覆盖（无需改代码）。若项目根目录存在 `.env` 文件，会先加载其中的变量（需安装 `python-dotenv`，已写在 requirements.txt 中）。

建议：复制 `.env.example` 为 `.env`，按需修改，之后直接运行 `python main.py` 即可生效。

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CRAWLER_BASE_URL` | 智云比分页面地址 | `https://live.nowscore.com/2in1.aspx` |
| `CRAWLER_DOWNLOAD_DIR` | 下载目录（crawl 保存 xls，merge_data / calc_car 也基于此目录） | 见 config.py |
| `CRAWLER_CUTOFF_HOUR` | 跨天临界点（0～23 时）。该时及之后 → 当日文件夹；该时之前 → 前一日文件夹 | `12` |
| `CRAWLER_TIMEZONE` | 用于“当前时间”的时区（决定下载目录/文件名） | `Asia/Shanghai` |
| `CRAWLER_HEADLESS` | `1` 无头模式，`0` 有浏览器界面 | `1` |

**.env 示例**（在项目根目录创建 `.env`，按需填写）：

```bash
# 跨天临界点（例如 12 点：12 点及以后算当天，12 点前算前一天）
# CRAWLER_CUTOFF_HOUR=12
# 下载与合并/计算使用的根目录
CRAWLER_DOWNLOAD_DIR=/path/to/足球彩票/北单
# 有界面运行（调试时可设为 0）
CRAWLER_HEADLESS=1
# 时区（一般不需改）
CRAWLER_TIMEZONE=Asia/Shanghai
```

**命令行临时覆盖示例**：

```bash
CRAWLER_HEADLESS=0 CRAWLER_DOWNLOAD_DIR=/path/to/excels python main.py
```

---

## 定时任务

建议使用**操作系统自带的定时任务**在以下整点自动执行 `python main.py`（抓取 → 合并 → 计算 → 曲线图）：

**触发时间（每天）**：2、4、6、15、17、19、21、23 点。

下面按系统说明如何配置。请将示例中的 **项目目录**、**Python 路径** 替换为你本机的实际路径。

### Windows（任务计划程序）

1. 打开 **任务计划程序**（`taskschd.msc` 或“开始”菜单搜索）。
2. 右侧 **“创建基本任务”**，名称如 `足球测评`，下一步。
3. 触发器选 **“每天”**，下一步。
4. 开始时间任选一天，如 `00:00:00`，重复间隔选 **“1 天”**，下一步。
5. 操作选 **“启动程序”**：
   - **程序或脚本**：本机 Python 解释器路径（若用虚拟环境，填项目下 `.venv\Scripts\python.exe`），例如：
     ```text
     D:\projects\football-betting-python\.venv\Scripts\python.exe
     ```
   - **添加参数**：`main.py`
   - **起始于**：项目根目录，例如：
     ```text
     D:\projects\football-betting-python
     ```
6. 完成创建后，在任务列表中双击该任务 → **“触发器”** 选项卡 → **“编辑”**。把“重复任务间隔”改为 **1 天**，并点击 **“新建”** 再添加 7 个触发器，开始时间分别设为当天 **02:00、04:00、06:00、15:00、17:00、19:00、21:00、23:00**（各一个，每天重复）。  
   或：创建 **8 个独立的基本任务**，每个任务只在一个时间点运行（2 点、4 点、…、23 点），程序与“起始于”同上。

**说明**：若 `.env` 放在项目根目录，任务计划程序会从该目录启动，一般能自动加载；否则可在该任务的“操作”里改为运行一个你自己写的 `.bat`，在 `.bat` 里先 `cd` 到项目目录再执行 `python main.py`。

---

### macOS（launchd）

1. 在项目根目录创建 plist 文件（或放在 `~/Library/LaunchAgents/`），例如 `com.football.crawler.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.football.crawler</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/你的用户名/Documents/cursor/football-betting-python/.venv/bin/python</string>
    <string>main.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/你的用户名/Documents/cursor/football-betting-python</string>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>2</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>4</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>/Users/你的用户名/Documents/cursor/football-log/football-betting-main.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/你的用户名/Documents/cursor/football-log/football-betting-main.err</string>
</dict>
</plist>
```

2. 将其中 **Python 路径**、**WorkingDirectory** 改为你本机的项目路径（若不用虚拟环境，`ProgramArguments` 第一项改为系统 `python3` 路径，如 `/usr/bin/python3`）。
3. 加载并启用：
   ```bash
   cp com.football.crawler.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.football.crawler.plist
   ```
4. 查看是否加载：`launchctl list | grep football`。停止：`launchctl unload ~/Library/LaunchAgents/com.football.crawler.plist`。

**常用管理命令（macOS launchd）**（若使用项目中的 `com.football.betting.main.plist`，将下面命令中的 plist 文件名替换为 `com.football.betting.main.plist`）：

```bash
# 查看定时任务是否已加载
launchctl list | grep football

# 停止定时任务（不再按点执行）
launchctl unload ~/Library/LaunchAgents/com.football.betting.main.plist

# 重新启用定时任务
launchctl load ~/Library/LaunchAgents/com.football.betting.main.plist
```

日志输出在 `/Users/zhiwuzou/Documents/cursor/football-log/football-betting-main.log`，错误在 `/Users/zhiwuzou/Documents/cursor/football-log/football-betting-main.err`。请先创建目录：`mkdir -p /Users/zhiwuzou/Documents/cursor/football-log`。

---

### Linux（cron）

1. 编辑当前用户 crontab：`crontab -e`。
2. 添加一行（整点 2、4、6、15、17、19、21、23 各执行一次）：

```cron
0 2,4,6,15,17,19,21,23 * * * /path/to/football-betting-python/.venv/bin/python /path/to/football-betting-python/main.py
```

或将 `python` 和 `main.py` 拆开，并保证在项目目录下执行：

```cron
0 2,4,6,15,17,19,21,23 * * * cd /path/to/football-betting-python && .venv/bin/python main.py
```

3. 将 `/path/to/football-betting-python` 替换为实际项目根目录；若未使用虚拟环境，改为系统 `python3` 路径。
4. 保存退出。cron 会按系统时区在每天 02:00、04:00、06:00、15:00、17:00、19:00、21:00、23:00 执行。

**查看日志**：若未重定向，cron 输出会发到用户邮件；可改为 `... main.py >> /tmp/football-crawler.log 2>&1` 便于排查。
