#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""个人版工作流：建 .ai/ 骨架，或检查它是否合规。

用法
    python task.py <项目目录>            建 .ai/TASK.md 和 .ai/REPORT.md，已存在则跳过
    python task.py <项目目录> --check    只检查，不改任何文件

退出码
    0  全部通过
    1  有必须修的问题
    2  还没收尾（没有 REPORT.md，只是提示）
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

## 分几步

- [ ] 1.1 <改哪个文件 / 做什么>
- [ ] 1.2 <改哪个文件 / 做什么>
- [ ] 1.3 <改哪个文件 / 做什么>

## 不做什么

- <范围外的事，避免做着做着跑偏>

## 放弃条件

- <出现什么情况就停；没有就写「不设」>
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

## 复盘

- 哪个判断错了：<哪个假设被证伪>
- 下次怎么改：<一条能执行的检查，不是「更仔细」>
- 进 rules.md 吗：<是 / 否>

## 没验的

- <什么没验> —— 因为 <原因>

## 下一步

- <可留空>
"""

AC_LINE = re.compile(r"^-\s*\[[ xX]\]\s*AC-(\d+)(.*)$", re.MULTILINE)
STEP_LINE = re.compile(r"^-\s*\[([ xX])\]\s*(\d+\.\d+)(.*)$", re.MULTILINE)
REPORT_ROW = re.compile(r"^\|\s*AC-(\d+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", re.MULTILINE)
SECTION_HEAD = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^[\s\-|#]*<[^<>\n]{1,40}>")

VALID_VERDICT = {"通过", "不通过", "未验"}
MIN_AC = 3
REVIEW_KEYS = ("判断", "下次", "rules")


def section(text: str, title: str) -> list[str]:
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
    for name, body in (("TASK.md", TASK_TEMPLATE), ("REPORT.md", REPORT_TEMPLATE)):
        p = ai / name
        if p.exists():
            print(f"[skip] {p.relative_to(root)} 已存在")
        else:
            p.write_text(body, encoding="utf-8", newline="\n")
            print(f"[new ] {p.relative_to(root)}")
    print("\n下一步：填 .ai/TASK.md 的「怎么算做完」和「分几步」，再动代码。")
    return 0


def check(root: Path) -> int:
    ai = root / ".ai"
    task_p, report_p = ai / "TASK.md", ai / "REPORT.md"
    problems: list[str] = []
    notes: list[str] = []

    if not task_p.exists():
        print("[!] 任务还没开始：没有 .ai/TASK.md")
        print(f"    先跑：python task.py {root}")
        return 2

    task = task_p.read_text(encoding="utf-8")
    acs = {int(m.group(1)) for m in AC_LINE.finditer(task)}
    steps = [(m.group(1), m.group(2)) for m in STEP_LINE.finditer(task)]
    undone = [n for flag, n in steps if flag == " "]

    if len(acs) < MIN_AC:
        problems.append(f"验收标准只有 {len(acs)} 条，至少要 {MIN_AC} 条")
    holes = placeholders(task)
    if holes:
        problems.append(f"TASK.md 还有 {len(holes)} 处占位符没填，例如：{holes[0]}")
    if len(steps) < 2:
        notes.append(f"只拆了 {len(steps)} 步，建议 2–6 步")
    if not any(ln.strip().strip("-").strip() for ln in section(task, "放弃条件")):
        notes.append("没写放弃条件——出了问题就没有止损线")
    print(f"[ok] TASK.md：{len(acs)} 条验收，{len(steps)} 步")

    if not report_p.exists():
        if undone:
            notes.append(f"还有 {len(undone)} 步没做（1.1 之类），正常")
        for msg in problems:
            print(f"[x] {msg}")
        for msg in notes:
            print(f"[!] {msg}")
        return 1 if problems else 2

    report = report_p.read_text(encoding="utf-8")
    rows = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
            for m in REPORT_ROW.finditer(report)}

    missing = sorted(acs - rows.keys())
    if missing:
        problems.append("报告里缺这些验收项：" + "、".join(f"AC-{n}" for n in missing))

    for n, (verdict, proof) in sorted(rows.items()):
        if verdict not in VALID_VERDICT:
            problems.append(f"AC-{n} 的结论写成「{verdict}」，只能是 通过 / 不通过 / 未验")
        elif verdict == "通过" and proof in ("", "—", "-"):
            problems.append(f"AC-{n} 说通过但没写证据")

    if undone:
        problems.append(f"还有 {len(undone)} 步没打勾就写了报告：{undone[0]}")

    review = "\n".join(section(report, "复盘"))
    lack = [k for k in REVIEW_KEYS if k not in review]
    if lack:
        problems.append("「复盘」缺这三样里的：" + "、".join(lack))

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
    for msg in notes:
        print(f"[!] {msg}")
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
