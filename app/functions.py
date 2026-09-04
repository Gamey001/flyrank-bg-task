import inngest

from app.client import inngest_client
from app.store import reports


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
        }
        return {"id": report_id, "result": result}

    return await ctx.step.run("build-report", build_report)


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


functions = [say_hello, make_report, heartbeat]
