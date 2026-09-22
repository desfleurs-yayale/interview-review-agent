#!/usr/bin/env python3
"""Send a Markdown summary to Feishu without shell interpolation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def find_lark_cli() -> tuple[str, dict[str, str]]:
    env = os.environ.copy()

    configured = env.get("INTERVIEW_AGENT_LARK_CLI")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return str(candidate), env
        raise RuntimeError("INTERVIEW_AGENT_LARK_CLI 指向的文件不存在")

    qwen_core = Path.home() / ".qwenworkcn/bin/ext/lark-cli-core-darwin-arm64"
    if qwen_core.is_file():
        env["QWORK_SHIM_ROUTE"] = "lark-cli"
        return str(qwen_core), env

    launcher = shutil.which("lark-cli")
    if not launcher:
        raise RuntimeError("未找到 lark-cli；请安装或设置 INTERVIEW_AGENT_LARK_CLI")

    resolved = Path(launcher).resolve()
    if resolved.name == "run.js" and resolved.parent.name == "scripts":
        native = resolved.parent.parent / "bin/lark-cli"
        if native.is_file():
            return str(native), env

    return launcher, env


def run_cli(binary: str, env: dict[str, str], args: list[str]) -> dict:
    completed = subprocess.run(
        [binary, *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"lark-cli 执行失败（{completed.returncode}）：{detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("lark-cli 未返回可解析的 JSON") from exc


def resolve_chat_id(
    binary: str, env: dict[str, str], chat_id: str | None, chat_name: str | None
) -> str:
    if chat_id:
        return chat_id
    if not chat_name:
        raise RuntimeError(
            "未配置目标群；请传 --chat-id/--chat-name，或设置 "
            "INTERVIEW_AGENT_FEISHU_CHAT_ID/INTERVIEW_AGENT_FEISHU_CHAT_NAME"
        )

    result = run_cli(
        binary,
        env,
        [
            "im",
            "+chat-search",
            "--query",
            chat_name,
            "--disable-search-by-user",
            "--as",
            "bot",
        ],
    )
    chats = result.get("data", {}).get("chats", [])
    exact = [chat for chat in chats if chat.get("name") == chat_name]
    if len(exact) != 1:
        raise RuntimeError(
            f"群名精确匹配结果为 {len(exact)} 个；请配置唯一的群 chat_id"
        )
    return exact[0]["chat_id"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从标准输入读取 Markdown 摘要并安全发送到飞书群"
    )
    parser.add_argument("--chat-id")
    parser.add_argument("--chat-name")
    parser.add_argument("--interview-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    message = sys.stdin.read()
    if not message.strip():
        raise RuntimeError("标准输入中的消息内容为空")

    chat_id = args.chat_id or os.environ.get("INTERVIEW_AGENT_FEISHU_CHAT_ID")
    chat_name = args.chat_name or os.environ.get("INTERVIEW_AGENT_FEISHU_CHAT_NAME")
    binary, env = find_lark_cli()
    target_chat_id = resolve_chat_id(binary, env, chat_id, chat_name)

    digest = hashlib.sha256(
        f"{args.interview_id}\0{message}".encode("utf-8")
    ).hexdigest()[:32]
    command = [
        "im",
        "+messages-send",
        "--chat-id",
        target_chat_id,
        "--markdown",
        message,
        "--idempotency-key",
        f"ia-{digest}",
        "--as",
        "bot",
    ]
    if args.dry_run:
        command.append("--dry-run")

    result = run_cli(binary, env, command)
    if not args.dry_run and result.get("ok") is not True:
        raise RuntimeError(f"飞书发送未成功：{json.dumps(result, ensure_ascii=False)}")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
