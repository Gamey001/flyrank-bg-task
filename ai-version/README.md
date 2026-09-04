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

`main_v2.py` declares app id `report-api` because prompt v2 asked for it — the same id as the
real app. Registering it against a Dev Server that already knows `app/` repoints that id at the
quarantine port, and the real app's jobs stop running until you `PUT /api/inngest` again. Run
one at a time.

The write-up is in the root README under "AI vs me".
