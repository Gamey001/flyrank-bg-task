import logging

import inngest

logging.basicConfig(level=logging.INFO)

inngest_client = inngest.Inngest(
    app_id="report-api",
    logger=logging.getLogger("report-api"),
    is_production=False,
)
