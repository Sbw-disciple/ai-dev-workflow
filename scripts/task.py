#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""个人版工作流：建 .ai/ 骨架，或检查它是否合规。

用法
    python task.py <项目目录>            建 .ai/TASK.md 和 .ai/REPORT.md，已存在则跳过
    python task.py <项目目录> --check    只检查，不改任何文件

退出码
    0  全部通过
    1  有必须修的问题
    2  还没收尾（没有 REPORT.md，或任务还没开始）

格式契约（写 .ai/ 时按这个来，脚本只认这个）
    验收项      - [ ] AC-1 一句话     列表符号 - * + 都行，缩进两格也行
    步骤        - [ ] 1.1 做什么（完成定义：做完怎么判断）
    报告表格    | AC-1 | 通过 | 证据 |   前面有空格也行
    代码块      围栏里的内容一律不参与检查（可以放心贴模板）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TASK_TEMPLATE = """# <任务名>

一句话目标：<只写结果，不写手段>

## 范围

**必须有**

- <少了这条就算没做成>

**明确不做**

- <这次明确不碰的>

**待定**

- 无

## 怎么算做完

- [ ] AC-1 <能判真假的一句话>
- [ ] AC-2 <能判真假的一句话>
- [ ] AC-3 <能判真假的一句话>

## 分几步

- [ ] 1.1 <做什么>（完成定义：<做完怎么判断>）
- [ ] 1.2 <做什么>（完成定义：<做完怎么判断>）
- [ ] 1.3 <做什么>（完成定义：<做完怎么判断>）

## 变更

| 时间 | 改了什么 | 为什么 | 谁同意 |
|---|---|---|---|
| — | — | — | — |

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

## 反向检查

- 该做没做的：<无 / 列出>
- 顺手多做的：<无 / 列出>

## 复盘

- 哪个判断错了：<哪个假设被证伪>
- 下次怎么改：<一条能执行的检查，不是「更仔细」>
- 进 rules.md 吗：<是 / 否>

## 没验的

- <什么没验> —— 因为 <原因>

## 下一步

- <可留空>
"""

# ---- 解析规则 ----------------------------------------------------------
# 允许行首缩进（Markdown 最多 3 个空格），列表符号允许 - * +
_ITEM = r"^[ \t]*[-*+][ \t]*\[([ xX])\][ \t]*"
AC_LINE = re.compile(_ITEM + r"AC-(\d+)(.*)$", re.MULTILINE)
STEP_LINE = re.compile(_ITEM + r"(\d+\.\d+)(.*)$", re.MULTILINE)
REPORT_ROW = re.compile(
    r"^[ \t]*\|[ \t]*AC-(\d+)[ \t]*\|[ \t]*([^|\n]*?)[ \t]*\|[ \t]*([^|\n]*?)[ \t]*\|",
    re.MULTILINE,
)
SECTION_HEAD = re.compile(r"^[ \t]{0,3}##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
SCOPE_HEAD = re.compile(r"^[ \t]{0,3}\*\*(.+?)\*\*[ \t]*$")
FENCE = re.compile(r"^[ \t]{0,3}(?:```|~~~)")
PLACEHOLDER = re.compile(r"^[\s\-|#*]*<[^<>\n]{1,40}>")

VALID_VERDICT = {"通过", "不通过", "未验"}
MIN_AC = 3
SCOPE_BLOCKS = ("必须有", "明确不做", "待定")
REVIEW_KEYS = ("判断", "下次", "rules")
UNVERIFIED_KEYS = ("——", "因为", "原因")
EMPTY_WORDS = {
    "", "无", "暂无", "没有", "暂时没有", "无待定", "空",
    "none", "n/a", "na", "—", "-", "nil", "无。",
}


def strip_code(text: str) -> str:
    """去掉围栏代码块的内容。贴模板、贴示例是最常见的动作，不能让它变成验收项。"""
    out: list[str] = []
    fenced = False
    for ln in text.splitlines():
        if FENCE.match(ln):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else ln)
    return "\n".join(out)


def section(text: str, title: str) -> list[str]:
    heads = list(SECTION_HEAD.finditer(text))
    for i, m in enumerate(heads):
        if m.group(1) == title:
            start = m.end()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return text[start:end].splitlines()
    return []


def bold_block(text: str, name: str) -> tuple[bool, list[str]]:
    """取出 **xxx** 下的行，返回 (是否存在, 行列表)。"""
    found, out, inside = False, [], False
    for ln in text.splitlines():
        if SECTION_HEAD.match(ln):
            inside = False
            continue
        m = SCOPE_HEAD.match(ln)
        if m:
            inside = m.group(1).strip() == name
            found = found or inside
            continue
        if inside:
            out.append(ln)
    return found, out


def item_body(line: str) -> str | None:
    """把 `- 无` / `* 暂无。` 这类行剥成正文；不是列表项返回 None。"""
    m = re.match(r"^[ \t]*[-*+][ \t]*(.*)$", line)
    return m.group(1) if m else None


def is_empty_item(line: str) -> bool:
    body = item_body(line)
    if body is None:
        return False
    return body.strip().rstrip("。.").lower() in EMPTY_WORDS


def placeholders(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if PLACEHOLDER.match(ln)]


# ---- 两个动作 ----------------------------------------------------------
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
    print("\n下一步：填 .ai/TASK.md 的「目标」「范围」「怎么算做完」「分几步」，再动代码。")
    return 0


def _report(label: str, summary: str, problems: list[str], notes: list[str]) -> None:
    mark = "[ok]" if not problems else "[x]"
    print(f"{mark} {label}：{summary}")
    for m in problems:
        print(f"[x] {m}")
    for m in notes:
        print(f"[!] {m}")


def check(root: Path) -> int:
    ai = root / ".ai"
    task_p, report_p = ai / "TASK.md", ai / "REPORT.md"

    if not task_p.exists():
        print("[!] 任务还没开始：没有 .ai/TASK.md")
        print(f"    先跑：python task.py {root}")
        return 2

    task = strip_code(task_p.read_text(encoding="utf-8"))
    # AC_LINE 的捕获组：1 = 勾选状态，2 = 编号，3 = 正文
    acs = {int(m.group(2)) for m in AC_LINE.finditer(task)}
    steps = [(m.group(1), m.group(2)) for m in STEP_LINE.finditer(task)]
    undone = [n for flag, n in steps if flag == " "]

    t_problems: list[str] = []
    t_notes: list[str] = []

    if len(acs) < MIN_AC:
        t_problems.append(f"验收标准只有 {len(acs)} 条，至少要 {MIN_AC} 条")
    holes = placeholders(task)
    if holes:
        t_problems.append(f"TASK.md 还有 {len(holes)} 处占位符没填，例如：{holes[0]}")

    missing_scope = [b for b in SCOPE_BLOCKS if not bold_block(task, b)[0]]
    if missing_scope:
        t_problems.append("「范围」缺这些节：" + "、".join(missing_scope))
    else:
        pending = [ln.strip() for ln in bold_block(task, "待定")[1]
                   if ln.strip().startswith(("-", "*", "+")) and not is_empty_item(ln)]
        if pending:
            t_problems.append(f"「待定」还有 {len(pending)} 项没定：{pending[0]}")

    if len(steps) < 2:
        t_notes.append(f"只拆了 {len(steps)} 步，建议 2–6 步")
    give_up = [ln.strip() for ln in section(task, "放弃条件")
               if ln.strip().startswith(("-", "*", "+")) and not is_empty_item(ln)]
    if not give_up:
        t_notes.append("没写放弃条件——出了问题就没有止损线")

    t_summary = f"{len(acs)} 条验收，{len(steps)} 步，范围{'齐' if not missing_scope else '不齐'}"

    if not report_p.exists():
        _report("TASK.md", t_summary, t_problems, t_notes)
        print("[!] 还没收尾：没有 .ai/REPORT.md")
        if undone:
            print(f"[!] 还有 {len(undone)} 步没做，正常")
        return 1 if t_problems else 2

    report = strip_code(report_p.read_text(encoding="utf-8"))
    rows = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
            for m in REPORT_ROW.finditer(report)}

    r_problems: list[str] = []
    r_notes: list[str] = []

    missing = sorted(acs - rows.keys())
    if missing:
        r_problems.append("报告里缺这些验收项：" + "、".join(f"AC-{n}" for n in missing))

    for n, (verdict, proof) in sorted(rows.items()):
        if verdict not in VALID_VERDICT:
            r_problems.append(f"AC-{n} 的结论写成「{verdict}」，只能是 通过 / 不通过 / 未验")
        elif verdict == "通过" and proof in ("", "—", "-", "无"):
            r_problems.append(f"AC-{n} 说通过但没写证据")

    if undone:
        r_problems.append(f"还有 {len(undone)} 步没打勾就写了报告：{undone[0]}")

    if not any(ln.strip() for ln in section(report, "反向检查")):
        r_problems.append("报告缺「反向检查」——该做没做、顺手多做的，各写一行")

    review_lines = section(report, "复盘")
    review = "\n".join(review_lines)
    lack = [k for k in REVIEW_KEYS if k not in review]
    if lack:
        r_problems.append("「复盘」缺这三样里的：" + "、".join(lack))
    else:
        empties = 0
        for ln in review_lines:
            body = item_body(ln)
            if body is None:
                continue
            for sep in ("：", ":"):
                if sep in body:
                    if is_empty_item("- " + body.split(sep, 1)[1]):
                        empties += 1
                    break
        if empties >= len(REVIEW_KEYS):
            r_notes.append("复盘三行全写成「无」——等于没复盘，至少写一条真的")

    holes = placeholders(report)
    if holes:
        r_problems.append(f"REPORT.md 还有 {len(holes)} 处占位符没填，例如：{holes[0]}")

    untested = [ln.strip() for ln in section(report, "没验的")
                if ln.strip().startswith(("-", "*", "+"))]
    for ln in untested:
        if is_empty_item(ln):
            continue
        if not any(k in ln for k in UNVERIFIED_KEYS):
            r_problems.append(f"「没验的」里有一条没写原因：{ln[:30]}")

    r_summary = f"{len(rows)} 条验收记录，{len(untested)} 条未验说明"

    _report("TASK.md", t_summary, t_problems, t_notes)
    _report("REPORT.md", r_summary, r_problems, r_notes)

    problems = t_problems + r_problems
    if not problems:
        print("[ok] 全部通过")
        return 0
    print(f"\n共 {len(problems)} 个问题，修完再跑一次。")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="个人版工作流：建 .ai/ 骨架或检查合规")
    ap.add_argument("project", nargs="?", default=".", help="项目根目录，默认当前目录")
    ap.add_argument("--check", action="store_true", help="只检查，不修改文件")
    ap.add_argument("--version", action="store_true", help="打印脚本版本")
    args = ap.parse_args()

    if args.version:
        print("task.py 0.8.0")
        return 0

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"[x] 目录不存在：{root}", file=sys.stderr)
        return 1
    return check(root) if args.check else init(root)


if __name__ == "__main__":
    sys.exit(main())
