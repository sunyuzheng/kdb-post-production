---
name: kdb-post-production
description: 给定视频文件或已有 SRT，自动完成转录→校对→断句→文章→高光→标题六步，产出可用字幕、高光分析和标题候选。课代表立正视频后期生产全链路。
type: Workflow
---

# 课代表立正 · 视频内容生产 Skill

## 目标输出

| 文件 | 用途 |
|------|------|
| `视频名.final.srt` | 导入剪辑软件的断句字幕 |
| `视频名.highlights.md` | 高光分析（中心命题 + 受众 + 叙事弧） |
| `视频名.titles.md` | 6-10 个标题候选 + 封面建议 |

所有文件生成在**视频同目录**。

## 代码库

`/Users/sunyuzheng/Desktop/AI/content/kedaibiao-srt-v2/`

所有命令在此目录下运行，使用 `venv/bin/python`。

## 运行方式

### 情况 A：从视频开始（全链路）

```bash
# 有嘉宾名 / 专有名词时注入（提高转录准确率）
venv/bin/python tools/process_video.py /path/to/视频.mp4 --seeds 嘉宾名

# 单口视频或不需要注入时
venv/bin/python tools/process_video.py /path/to/视频.mp4 --no-seeds
```

防止 Mac 休眠（长视频建议加）：

```bash
caffeinate -i venv/bin/python tools/process_video.py 视频.mp4 --no-seeds
```

### 情况 B：已有 SRT，只需高光 + 标题

```bash
venv/bin/python tools/generate_highlights.py /path/to/视频名.final.srt
venv/bin/python tools/generate_titles.py /path/to/视频名.article.md
```

### 情况 C：只需标题（已有 highlights）

```bash
venv/bin/python tools/generate_titles.py /path/to/视频名.article.md
```

## 验收标准

- `titles.md` 存在，包含 ≥6 个标题候选，每个有一句话说明
- `titles.md` 包含封面建议（访谈：3句金句；单口：3-10字冲击文字）
- `highlights.md` 存在，包含中心命题、受众分析、≥3 段高光（每段有原话引用 + 叙事位置 + 好奇钩子）
- 标题无 AI 公文感，无空洞承诺，每条有具体内容锚点

## 已知陷阱

| 问题 | 处理方式 |
|------|---------|
| 后台运行时交互式输入卡住 | 始终用 `--seeds` 或 `--no-seeds`，禁止用交互模式 |
| 高光选了戏剧性时刻而非叙事核心 | 在 `.final.srt` 末尾手动追加高光字幕，系统自动优先使用亲选片段 |
| 标题生成步骤报错 `claude not found` | 需提前安装并登录 Claude Code CLI：`which claude` 确认 |
| 嘉宾名仍转录出错 | `--seeds` 用书面正确写法；校对阶段会报告名字出现次数，未找到则需手动查找 |

## 关键设计

**高光驱动标题**：`generate_titles.py` 先读 `highlights.md`，标题描述高光背后更大的问题，而非高光本身——高光让观众感觉「这期有料」，标题创造点击动机。

**三轮标题工作流**：Round 0 资深编辑发散生成 → Round 1 独立评审对比频道 Top 25 真实高播标题（`data/top_titles.txt`）找盲区 → Round 2 终审按指令补强并选定。

**时间参考**：8 分钟视频全链路约 15-20 分钟；30 分钟视频约 25-40 分钟。步骤 1-3 完全离线，步骤 5-6 调用 Claude Code CLI（Opus），每期约 ¥3-8。
