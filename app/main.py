import uuid

import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from app.client import inngest_client
from app.functions import functions
from app.store import reports

app = FastAPI(title="Report API")


class ReportRequest(BaseModel):
    topic: str = ""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(body: ReportRequest) -> dict[str, str]:
    topic = body.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = uuid.uuid4().hex[:8]
    reports[report_id] = {"id": report_id, "topic": topic, "status": "pending"}

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": topic},
        )
    )
    return {"id": report_id, "status": "pending"}


@app.get("/reports")
def list_reports() -> list[dict]:
    return list(reports.values())


@app.get("/reports/{report_id}")
def get_report(report_id: str) -> dict:
    report = reports.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


inngest.fast_api.serve(app, inngest_client, functions)
