import inngest.fast_api
from fastapi import FastAPI

from app.client import inngest_client
from app.functions import functions

app = FastAPI(title="Report API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


inngest.fast_api.serve(app, inngest_client, functions)
