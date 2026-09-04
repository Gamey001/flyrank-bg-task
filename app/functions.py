import inngest

from app.client import inngest_client


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-moment", 5_000)
    return "Hello from the background!"


functions = [say_hello]
