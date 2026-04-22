#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件响应模式 Claude CLI 工具

原则（来自 gist.github.com/grapeot/9cbdcf7f26bd1d69a11c39414b54dbe6）：
  - 文件模式 > pipe 模式：Claude 的心理模型是"完成工作并保存"，而非"对话回答"，不会截断
  - 大内容通过文件传递，绕过 CLI 参数长度限制
  - --permission-mode bypassPermissions 用于自动化流水线
"""

import subprocess
import tempfile
from pathlib import Path

DEFAULT_MODEL = "claude-opus-4-6"


def call_claude_file_based(
    prompt: str,
    output_path: Path,
    model: str = DEFAULT_MODEL,
    timeout: int = 900,
) -> str:
    """
    文件响应模式：将 prompt 写入临时文件，让 Claude 直接将完整输出写入 output_path。

    Args:
        prompt:      完整任务描述（包含上下文内容，可以很大）
        output_path: Claude 将写入结果的目标文件
        model:       Claude 模型，默认 claude-opus-4-6
        timeout:     subprocess 超时秒数

    Returns:
        output_path 写入的内容字符串

    Raises:
        RuntimeError: Claude 调用失败或未生成输出文件
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False,
        encoding="utf-8", prefix="kdb_task_",
    ) as f:
        f.write(prompt)
        task_file = Path(f.name)

    try:
        instruction = (
            f"Read all task instructions and content from {task_file}. "
            f"Write your complete response directly to {output_path}. "
            f"Do not output anything to the terminal — write only to the file."
        )
        result = subprocess.run(
            [
                "claude",
                "--permission-mode", "bypassPermissions",
                "--model", model,
                "-p", instruction,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude 失败 (exit {result.returncode}): {result.stderr[:400]}"
            )
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Claude 未写入输出文件: {output_path}")

        return output_path.read_text(encoding="utf-8")
    finally:
        task_file.unlink(missing_ok=True)
