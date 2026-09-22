# Project rules

- Never commit recordings, raw transcripts, real interview reviews, credentials, chat IDs, private paths, IP addresses, or personal identifiers.
- Keep provider-specific behavior behind configuration or adapters.
- Do not overwrite existing transcripts or reviews.
- Validate skills, run `python3 -m unittest discover -s tests`, and run the privacy scan before opening a pull request.
- Use the workflow: branch -> commit -> push -> pull request -> user review. Do not merge without explicit user approval.
