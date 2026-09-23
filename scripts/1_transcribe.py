#!/usr/bin/env python3
"""Transcribe one interview recording with local FunASR.

Usage:
    python3 scripts/1_transcribe.py AUDIO [OUTPUT]

When OUTPUT is omitted, the script writes <audio-stem>_speakers.txt in the
current directory. Existing files are never overwritten; -2, -3, ... is added.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time


# Model-level decoding hints. Replace these examples with your own vocabulary.
HOTWORDS = [
    "产品经理",
    "用户增长",
    "转化率",
    "留存率",
    "DAU",
]

# Optional exact replacements applied after decoding. Keep this list small and
# review every rule: broad replacements can silently change transcript facts.
POSTPROCESS_HOTWORD_MAP = {
    "CRI": "CLI",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用本地 FunASR 生成带时间戳和说话人标签的逐字稿"
    )
    parser.add_argument("audio", type=Path, help="输入音频文件")
    parser.add_argument("output", type=Path, nargs="?", help="输出文本文件")
    return parser.parse_args()


def non_overwriting_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def apply_replacements(text: str) -> tuple[str, list[tuple[str, str]]]:
    matches: list[tuple[str, str]] = []
    for source, target in POSTPROCESS_HOTWORD_MAP.items():
        if source in text:
            text = text.replace(source, target)
            matches.append((source, target))
    return text, matches


def main() -> int:
    args = parse_args()
    audio = args.audio.expanduser().resolve()
    if not audio.is_file():
        raise SystemExit(f"找不到音频文件: {audio}")

    requested_output = args.output or Path(f"{audio.stem}_speakers.txt")
    output = non_overwriting_path(requested_output.expanduser().resolve())
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        from funasr import AutoModel
    except ImportError as exc:
        raise SystemExit("未安装 FunASR；请先在本地 Python 环境中安装 funasr") from exc

    print("正在加载 ASR、VAD、标点和说话人模型……")
    started_at = time.time()
    model = AutoModel(
        model="paraformer-zh",
        vad_model="fsmn-vad",
        punc_model="ct-punc",
        spk_model="cam++",
        device="cpu",
    )

    result = model.generate(
        input=str(audio),
        batch_size_s=300,
        hotword=" ".join(HOTWORDS),
    )
    if not result:
        raise SystemExit("FunASR 没有返回转写结果")

    lines: list[str] = []
    replacements: list[tuple[str, str]] = []
    sentence_info = result[0].get("sentence_info", [])
    if sentence_info:
        for item in sentence_info:
            speaker = item.get("spk", 0)
            start = item.get("start", 0) / 1000.0
            end = item.get("end", 0) / 1000.0
            text, matched = apply_replacements(item.get("text", "").strip())
            replacements.extend(matched)
            lines.append(f"[说话人 {speaker}] ({start:.1f}s -> {end:.1f}s): {text}")
    else:
        text, matched = apply_replacements(result[0].get("text", "").strip())
        replacements.extend(matched)
        lines.append(text)

    output.write_text("\n".join(lines), encoding="utf-8")
    elapsed = time.time() - started_at
    print(f"转写完成，耗时 {elapsed:.2f} 秒")
    print(f"输出文件: {output}")
    if replacements:
        unique = sorted(set(replacements))
        print("文本纠错命中: " + ", ".join(f"{a} -> {b}" for a, b in unique))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

