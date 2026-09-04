"""Generated from PROMPT.md v2, after the v1 run failed the Stage 3 checkpoint."""

import logging
import uuid

import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

inngest_client = inngest.Inngest(
    app_id="report-api",
    logger=logging.getLogger("report-api"),
    is_production=False,
)

reports: dict[str, dict] = {}

app = FastAPI()


class ReportRequest(BaseModel):
    topic: str = ""


@app.post("/reports", status_code=202)
async def create_report(request: ReportRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": topic, "status": "pending"}

    await inngest_client.send(
        inngest.Event(name="report/requested", data={"id": report_id, "topic": topic})
    )
    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports[report_id]


async def on_report_failed(ctx: inngest.Context) -> None:
    failed_id = ctx.event.data.get("event", {}).get("data", {}).get("id")
    if failed_id in reports:
        reports[failed_id]["status"] = "failed"


@inngest_client.create_function(
    fn_id="make-report",
    on_failure=on_report_failed,
    retries=2,
    trigger=inngest.TriggerEvent(event="report/requested"),
)
async def make_report(ctx: inngest.Context):
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    await ctx.step.sleep("slow-work", 8000)

    async def build():
        if topic == "fail":
            raise Exception("Report generation failed")

        result = f"Report about {topic}"
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result
        return result

    return await ctx.step.run("build-report", build)


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context):
    pending = len([r for r in reports.values() if r["status"] == "pending"])
    done = len([r for r in reports.values() if r["status"] == "done"])
    failed = len([r for r in reports.values() if r["status"] == "failed"])

    ctx.logger.info(f"Reports: {pending} pending, {done} done, {failed} failed")


inngest.fast_api.serve(app, inngest_client, [make_report, heartbeat])
