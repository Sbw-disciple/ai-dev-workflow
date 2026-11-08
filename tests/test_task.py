#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""task.py 的回归测试。只用标准库。

跑：python tests/test_task.py      （或 python -m unittest discover -s tests）
"""
from __future__ import annotations

import importlib.util
import io
import pathlib
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "task.py"

TASK = """# 试解析
一句话目标：测试解析器的容错边界。

## 范围

**必须有**

- 甲

**明确不做**

- 乙

**待定**

- 无

## 怎么算做完

- [x] AC-1 甲成立
- [x] AC-2 乙不成立
- [x] AC-3 丙成立

## 分几步

- [x] 1.1 做甲（完成定义：能跑）
- [x] 1.2 做乙（完成定义：能跑）

## 变更

| 时间 | 改了什么 | 为什么 | 谁同意 |
|---|---|---|---|
| — | — | — | — |

## 放弃条件

- 不设
"""

REPORT = """# 完成报告 · 试解析

日期：2026-11-08 19:10

## 改了什么

- `a.py` — 加了甲

## 验收

| 编号 | 结论 | 证据 |
|---|---|---|
| AC-1 | 通过 | 跑了一次 exit 0 |
| AC-2 | 通过 | 跑了一次 exit 0 |
| AC-3 | 通过 | 跑了一次 exit 0 |

## 反向检查

- 该做没做的：无
- 顺手多做的：无

## 复盘

- 哪个判断错了：以为解析器够用
- 下次怎么改：先写探针再改代码
- 进 rules.md 吗：是

## 没验的

- Python 3.9 下没跑 —— 因为本机只有 3.14

## 下一步

- 无
"""


def load_module():
    spec = importlib.util.spec_from_file_location("task_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TaskCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def setUp(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="taskpy-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    # --- 工具 ---
    def write(self, task: str | None, report: str | None, newline: str = "\n") -> None:
        ai = self.root / ".ai"
        ai.mkdir(parents=True, exist_ok=True)
        for name, txt in (("TASK.md", task), ("REPORT.md", report)):
            if txt is None:
                continue
            body = txt.replace("\n", newline).encode("utf-8")
            (ai / name).write_bytes(body)

    def check(self) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.mod.check(self.root)
        return code, buf.getvalue()

    def assertCode(self, want: int, must: str | None = None) -> str:
        code, out = self.check()
        self.assertEqual(code, want, msg=f"退出码 {code} != {want}\n{out}")
        if must:
            self.assertIn(must, out)
        return out

    # --- 基础状态 ---
    def test_empty_dir_is_not_started(self) -> None:
        self.assertCode(2, "任务还没开始")

    def test_init_creates_both_files(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(self.mod.init(self.root), 0)
        self.assertTrue((self.root / ".ai" / "TASK.md").exists())
        self.assertTrue((self.root / ".ai" / "REPORT.md").exists())

    def test_init_is_idempotent_and_never_overwrites(self) -> None:
        with redirect_stdout(io.StringIO()):
            self.mod.init(self.root)
        p = self.root / ".ai" / "TASK.md"
        p.write_text("# 我填过的\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.mod.init(self.root)
        self.assertEqual(p.read_text(encoding="utf-8"), "# 我填过的\n")
        self.assertIn("[skip]", buf.getvalue())

    def test_fresh_template_fails_on_placeholders(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.mod.init(self.root)
        self.assertCode(1, "占位符")

    def test_complete_pair_passes(self) -> None:
        self.write(TASK, REPORT)
        self.assertCode(0, "全部通过")

    # --- 之前找出来的四个 bug ---
    def test_pending_written_as_zanwu_is_clear(self) -> None:
        for word in ("暂无", "暂时没有", "没有。", "无"):
            with self.subTest(word=word):
                self.write(TASK.replace("**待定**\n\n- 无", f"**待定**\n\n- {word}"), REPORT)
                self.assertCode(0, "全部通过")

    def test_pending_really_unclear_still_fails(self) -> None:
        self.write(TASK.replace("**待定**\n\n- 无", "**待定**\n\n- 要不要加通知"), REPORT)
        self.assertCode(1, "还有 1 项没定")

    def test_star_and_plus_bullets_are_parsed(self) -> None:
        for bullet in ("*", "+"):
            with self.subTest(bullet=bullet):
                self.write(TASK.replace("- [x] AC-", f"{bullet} [x] AC-"), REPORT)
                code, out = self.check()
                self.assertEqual(code, 0, msg=out)
                self.assertIn("3 条验收", out)

    def test_code_fence_is_ignored(self) -> None:
        extra = "\n示例：\n\n```markdown\n- [ ] AC-9 <新验收>\n- [ ] 9.9 <某步>\n```\n"
        self.write(TASK + extra, REPORT)
        code, out = self.check()
        self.assertEqual(code, 0, msg=out)
        self.assertIn("3 条验收", out)
        self.assertNotIn("AC-9", out)

    def test_indented_table_row_is_parsed(self) -> None:
        self.write(TASK, REPORT.replace("| AC-2", "  | AC-2"))
        self.assertCode(0, "全部通过")

    def test_indented_heading_is_parsed(self) -> None:
        self.write(TASK.replace("## 怎么算做完", "  ## 怎么算做完"), REPORT)
        self.assertCode(0, "全部通过")

    # --- 原有规则仍然生效 ---
    def test_too_few_acceptance_items(self) -> None:
        self.write(TASK.replace("- [x] AC-3 丙成立\n", ""), REPORT)
        self.assertCode(1, "至少要 3 条")

    def test_missing_scope_block(self) -> None:
        self.write(TASK.replace("**必须有**\n\n- 甲\n", ""), REPORT)
        self.assertCode(1, "范围」缺这些节")

    def test_report_missing_one_item(self) -> None:
        self.write(TASK, "\n".join(l for l in REPORT.splitlines() if not l.startswith("| AC-3")))
        self.assertCode(1, "AC-3")

    def test_pass_without_evidence(self) -> None:
        self.write(TASK, REPORT.replace("| AC-1 | 通过 | 跑了一次 exit 0 |", "| AC-1 | 通过 | — |"))
        self.assertCode(1, "说通过但没写证据")

    def test_unchecked_step_blocks_report(self) -> None:
        self.write(TASK.replace("- [x] 1.2", "- [ ] 1.2"), REPORT)
        self.assertCode(1, "没打勾")

    def test_missing_reverse_check(self) -> None:
        self.write(TASK, REPORT.replace("## 反向检查", "## 附注"))
        self.assertCode(1, "反向检查")

    def test_missing_retro_section(self) -> None:
        self.write(TASK, REPORT.replace("## 复盘", "## 备注"))
        self.assertCode(1, "复盘")

    def test_unverified_without_reason(self) -> None:
        self.write(TASK, REPORT.replace(" —— 因为本机只有 3.14", ""))
        self.assertCode(1, "没写原因")

    def test_unverified_written_as_none_is_allowed(self) -> None:
        self.write(TASK, REPORT.replace("- Python 3.9 下没跑 —— 因为本机只有 3.14", "- 无"))
        self.assertCode(0, "全部通过")

    def test_empty_retro_is_note_not_error(self) -> None:
        empty = "## 复盘\n\n- 哪个判断错了：无\n- 下次怎么改：无\n- 进 rules.md 吗：无\n"
        start = REPORT.index("## 复盘")
        end = REPORT.index("## 没验的")
        self.write(TASK, REPORT[:start] + empty + "\n" + REPORT[end:])
        code, out = self.check()
        self.assertEqual(code, 0, msg=out)
        self.assertIn("等于没复盘", out)

    def test_crlf_is_fine(self) -> None:
        self.write(TASK, REPORT, newline="\r\n")
        self.assertCode(0, "全部通过")

    def test_no_report_means_unfinished(self) -> None:
        self.write(TASK, None)
        self.assertCode(2, "还没收尾")

    def test_task_problems_win_over_unfinished(self) -> None:
        self.write(TASK.replace("- [x] AC-3 丙成立\n", ""), None)
        self.assertCode(1, "至少要 3 条")

    def test_ok_mark_disappears_when_section_has_problems(self) -> None:
        self.write(TASK.replace("- [x] AC-3 丙成立\n", ""), REPORT)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertNotIn("[ok] TASK.md", out)


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=1))
