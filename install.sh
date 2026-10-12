#!/usr/bin/env bash
# Run from the cloned repository: bash install.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
trap 'echo "安装中断：请检查上方错误，修复后重新运行 bash install.sh。" >&2' ERR

command -v python3 >/dev/null || { echo "请先安装 Python 3.10 或更高版本。" >&2; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "需要 Python 3.10 或更高版本")'
if ! command -v ffmpeg >/dev/null; then
  echo "缺少 FFmpeg。Mac 安装命令：brew install ffmpeg"
  echo "安装完成后重新运行 bash install.sh。"
  exit 1
fi

echo "创建项目 Python 环境并安装依赖……"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt torch torchaudio modelscope
.venv/bin/python -c 'from funasr import AutoModel; import torch, torchaudio, modelscope'
.venv/bin/python scripts/1_transcribe.py --help >/dev/null

if [ ! -e .env ]; then
  cp .env.example .env
  chmod 600 .env
  echo "已创建 .env，请填写录音目录和知识库目录；路径含空格时请使用引号。"
else
  echo "保留已有 .env 配置。"
fi

echo "本地依赖检查通过。尚未下载模型，也尚未验证真实音频。"
echo "下一步：编辑 .env，然后运行 bash scripts/run-transcribe.sh 音频路径 输出路径"
echo "Skill 导入、AI 复盘和定时任务请按 docs/setup.md 在所选 AI 工具中配置。"
