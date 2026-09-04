# Quarantine

AI-generated code. Not the submission — the hand-built version lives in `app/`.

- `PROMPT.md` — the prompt I wrote from memory (v1) and the improved one (v2).
- `main.py` — what v1 produced.
- `main_v2.py` — what v2 produced after v1 failed the Stage 3 checkpoint.

Run either against the same Dev Server:

```bash
.venv/bin/uvicorn main:app --port 8001      # or main_v2:app
curl -X PUT http://localhost:8001/api/inngest   # register it with the Dev Server
```

The write-up is in the root README under "AI vs me".
