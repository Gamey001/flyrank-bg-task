import time
from pathlib import Path

import inngest

from app.client import inngest_client
from app.store import reports

OUTBOX = Path("outbox")


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-moment", 5_000)
    return "Hello from the background!"


async def mark_failed(ctx: inngest.Context) -> None:
    original = ctx.event.data.get("event", {}).get("data", {})
    report = reports.get(str(original.get("id")))
    if report is not None:
        report["status"] = "failed"


@inngest_client.create_function(
    fn_id="make-report",
    on_failure=mark_failed,
    retries=2,
    trigger=inngest.TriggerEvent(event="report/requested"),
)
async def make_report(ctx: inngest.Context) -> dict[str, str]:
    report_id = str(ctx.event.data["id"])
    topic = str(ctx.event.data["topic"])

    await ctx.step.sleep("do-the-slow-work", 8_000)

    async def build_report() -> dict[str, str]:
        if topic == "fail":
            raise RuntimeError("The report oven is broken!")

        result = f"Report on {topic}: 3 findings, 2 recommendations."
        reports[report_id] = {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": result,
            "done_at": time.time(),
        }
        return {"id": report_id, "result": result}

    built = await ctx.step.run("build-report", build_report)

    async def deliver() -> str:
        OUTBOX.mkdir(exist_ok=True)
        path = OUTBOX / f"{report_id}.txt"
        path.write_text(f"Subject: your report on {topic}\n\n{built['result']}\n")
        return str(path)

    await ctx.step.run("send-the-email", deliver)
    return built


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> str:
    counts = {"pending": 0, "done": 0, "failed": 0}
    for report in reports.values():
        counts[report["status"]] = counts.get(report["status"], 0) + 1

    line = f"heartbeat: {counts['pending']} pending, {counts['done']} done, {counts['failed']} failed"
    ctx.logger.info(line)
    return line


@inngest_client.create_function(
    fn_id="cleanup",
    trigger=inngest.TriggerCron(cron="*/5 * * * *"),
)
async def cleanup(ctx: inngest.Context) -> str:
    cutoff = time.time() - 600
    stale = [
        report_id
        for report_id, report in reports.items()
        if report["status"] == "done" and report.get("done_at", 0) < cutoff
    ]
    for report_id in stale:
        del reports[report_id]

    line = f"cleanup: removed {len(stale)} done reports older than 10 minutes"
    ctx.logger.info(line)
    return line


functions = [say_hello, make_report, heartbeat, cleanup]
