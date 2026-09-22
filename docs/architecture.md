# Architecture

## Components

1. **Capture**: a phone shortcut or any sync mechanism places an audio file in `INTERVIEW_AUDIO_DIR`.
2. **Detection**: a scheduler scans for stable, unprocessed audio files.
3. **Transcription**: `interview-transcribe` calls a user-provided local FunASR adapter and writes `<base>_speakers.txt`.
4. **Review**: `interview-review` reads the entire transcript and writes one structured Markdown review without an intermediate JSON file.
5. **Orchestration**: `interview-agent` resumes from the first missing valid artifact instead of repeating completed work.
6. **Notification**: the optional Feishu/Lark adapter sends only a short summary and the review location.

## State and idempotency

- Existing transcripts and reviews are never overwritten.
- Repeated output names receive `-2`, `-3`, and so on.
- A valid transcript allows the workflow to resume from review.
- A valid review allows notification without retranscription or regeneration.
- Notification uses a deterministic idempotency key derived from the interview ID and message content.

## Trust boundaries

- Audio and transcripts stay local unless the user deliberately sends them elsewhere.
- The AI model sees the transcript during review, according to the selected AI provider's execution model.
- Notifications contain a summary, not the full transcript.
- Provider-specific paths and credentials remain local configuration.

