# Prompt v1

Written from memory, without looking at the assignment brief.

> Build a Python service with FastAPI that generates reports in the background using Inngest.
>
> - `POST /reports` takes a JSON body with a topic. It must answer straight away with 202 and
>   an id — it must not wait for the report to be made.
> - Making a report takes about 8 seconds. Do that in an Inngest function triggered by an
>   event, using a sleep step followed by a step that builds the result and saves it.
> - `GET /reports/{id}` returns the report: pending at first, then done with the result. An
>   unknown id gives 404.
> - If the topic is missing, return 400 and don't start a job.
> - The background function should retry twice when it fails.
> - Add an Inngest cron function that runs every minute and logs how many reports are pending,
>   done and failed.
>
> Keep the reports in memory. Put it all in one file.

# Prompt v2 — the rematch

Same as above, plus the three things v1 left the AI to guess:

> - A missing **or blank** topic must return exactly `400`, not FastAPI's default validation
>   error, and the event must not be sent.
> - A report must actually be able to reach the `failed` state — when the function runs out of
>   retries, mark that report `failed` so the cron's count means something.
> - Serve the Inngest functions at `/api/inngest` on port 8000, with app id `report-api`.
