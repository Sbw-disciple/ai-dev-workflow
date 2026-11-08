#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""个人版工作流：建 .ai/ 骨架，或检查它是否合规。

用法
    python task.py <项目目录>            建 .ai/TASK.md 和 .ai/REPORT.md，已存在则跳过
    python task.py <项目目录> --check    只检查，不改任何文件

退出码
    0  全部通过
    1  有必须修的问题
    2  任务还没开始或还没收尾（只是提示，不是错误）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TASK_TEMPLATE = """# <任务名>

一句话：<这次要达成什么>

## 怎么算做完

- [ ] AC-1 <能判真假的一句话>
- [ ] AC-2 <能判真假的一句话>
- [ ] AC-3 <能判真假的一句话>

## 不做什么

- <范围外的事，避免做着做着跑偏>

## 假设

- <没问就自己定的东西>
"""

REPORT_TEMPLATE = """# 完成报告 · <任务名>

日期：<yyyy-MM-dd HH:mm>

## 改了什么

- <文件路径> — <一句话>

## 验收

| 编号 | 结论 | 证据 |
|---|---|---|
| AC-1 | 未验 | — |
| AC-2 | 未验 | — |
| AC-3 | 未验 | — |

## 没验的

- <什么没验> —— 因为 <原因>

## 下一步

- <可留空>
"""

AC_LINE = re.compile(r"^-\s*\[[ xX]\]\s*AC-(\d+)(.*)$", re.MULTILINE)
REPORT_ROW = re.compile(r"^\|\s*AC-(\d+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", re.MULTILINE)
SECTION_HEAD = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^[\s\-|#]*<[^<>\n]{1,40}>")

VALID_VERDICT = {"通过", "不通过", "未验"}
MIN_AC = 3


def section(text: str, title: str) -> list[str]:
    """取出某个二级标题下的正文行；没有这一节返回空列表。"""
    heads = list(SECTION_HEAD.finditer(text))
    for i, m in enumerate(heads):
        if m.group(1) == title:
            start = m.end()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return text[start:end].splitlines()
    return []


def placeholders(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if PLACEHOLDER.match(ln)]


def init(root: Path) -> int:
    ai = root / ".ai"
    ai.mkdir(parents=True, exist_ok=True)
    made = []
    for name, body in (("TASK.md", TASK_TEMPLATE), ("REPORT.md", REPORT_TEMPLATE)):
        p = ai / name
        if p.exists():
            print(f"[skip] {p.relative_to(root)} 已存在")
        else:
            p.write_text(body, encoding="utf-8", newline="\n")
            made.append(p.relative_to(root))
            print(f"[new ] {p.relative_to(root)}")
    print("\n下一步：填 .ai/TASK.md 的「怎么算做完」，至少 3 条能判真假的。")
    return 0


def check(root: Path) -> int:
    ai = root / ".ai"
    task_p, report_p = ai / "TASK.md", ai / "REPORT.md"
    problems: list[str] = []
    notes: list[str] = []

    if not task_p.exists():
        print("[!] 任务还没开始：没有 .ai/TASK.md")
        print("    先跑：python task.py %s" % root)
        return 2

    task = task_p.read_text(encoding="utf-8")
    acs = {int(m.group(1)): m.group(2).strip() for m in AC_LINE.finditer(task)}

    if len(acs) < MIN_AC:
        problems.append(f"验收标准只有 {len(acs)} 条，至少要 {MIN_AC} 条")
    holes = placeholders(task)
    if holes:
        problems.append(f"TASK.md 还有 {len(holes)} 处占位符没填，例如：{holes[0]}")
    print(f"[ok] TASK.md：{len(acs)} 条验收标准")

    if not report_p.exists():
        notes.append("任务还没收尾：没有 .ai/REPORT.md")
        for msg in problems:
            print(f"[x] {msg}")
        for msg in notes:
            print(f"[!] {msg}")
        return 1 if problems else 2

    report = report_p.read_text(encoding="utf-8")
    rows = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
            for m in REPORT_ROW.finditer(report)}

    missing = sorted(set(acs) - set(rows))
    if missing:
        problems.append("报告里缺这些验收项：" + "、".join(f"AC-{n}" for n in missing))

    for n, (verdict, proof) in sorted(rows.items()):
        if verdict not in VALID_VERDICT:
            problems.append(f"AC-{n} 的结论写成「{verdict}」，只能是 通过 / 不通过 / 未验")
        elif verdict == "通过" and proof in ("", "—", "-"):
            problems.append(f"AC-{n} 说通过但没写证据")

    holes = placeholders(report)
    if holes:
        problems.append(f"REPORT.md 还有 {len(holes)} 处占位符没填，例如：{holes[0]}")

    untested = [ln.strip() for ln in section(report, "没验的") if ln.strip().startswith("-")]
    for ln in untested:
        if not any(k in ln for k in ("——", "因为", "原因")):
            problems.append(f"「没验的」里有一条没写原因：{ln[:30]}")

    print(f"[ok] REPORT.md：{len(rows)} 条验收记录，{len(untested)} 条未验说明")

    for msg in problems:
        print(f"[x] {msg}")
    if not problems:
        print("[ok] 全部通过")
        return 0
    print(f"\n共 {len(problems)} 个问题，修完再跑一次。")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="个人版工作流：建 .ai/ 骨架或检查合规")
    ap.add_argument("project", nargs="?", default=".", help="项目根目录，默认当前目录")
    ap.add_argument("--check", action="store_true", help="只检查，不修改文件")
    args = ap.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"[x] 目录不存在：{root}", file=sys.stderr)
        return 1
    return check(root) if args.check else init(root)


if __name__ == "__main__":
    sys.exit(main())
