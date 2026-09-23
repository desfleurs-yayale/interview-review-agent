# Setup

## 1. Prepare local transcription

Install FunASR in a local Python environment with `python3 -m pip install -r requirements.txt`. The repository includes a portable starting point at `scripts/1_transcribe.py`; its contract is:

```text
python3 1_transcribe.py <audio-path> <output-path>
python3 1_transcribe.py <audio-path>
```

The result is a non-empty UTF-8 text file with speaker labels when the selected FunASR models return `sentence_info`. Configure its path with `INTERVIEW_TRANSCRIBE_SCRIPT`. The first run may download the configured models.

Edit `HOTWORDS` and `POSTPROCESS_HOTWORD_MAP` in your local copy when domain vocabulary needs tuning. Review replacement rules carefully because post-processing changes transcript text.

## 2. Prepare the Markdown vault

Create an Inbox for transcripts and a Reviews directory for generated Markdown. Configure the vault and relative directories in `.env`.

Suggested portable defaults:

```text
Interview/Inbox
Interview/Reviews
```

Emoji folder names also work, but are intentionally not required by the public package.

## 3. Install the Skills

Install the three directories under `skills/` in the AI environment of your choice. The environment must be able to read local files and invoke the transcription script.

The `.env.example` file is a configuration template. Export its values in the shell or configure equivalent environment variables in the AI workspace; the scripts intentionally do not load `.env` automatically.

## 4. Optional notification

The included sender supports a configured `lark-cli`. Set either a unique chat ID or an exact chat name. Keep IDs and credentials in local environment variables, never in the Skill package.

## 5. Schedule checks

Use the scheduler provided by your AI workspace or the operating system. A safe scheduled prompt should:

- scan only the configured recording directory;
- ignore files whose size or modification time is still changing;
- stop quietly when there is no new recording;
- resume from an existing transcript or review;
- never delete recordings, transcripts, reviews, or memory files.
