from fastapi import FastAPI
from app.api.routes import health, posture, snore


app = FastAPI(
    title="Sleep Intelligence REST API",
    description=(
        "Advanced REST API for sleep tracking analysis, posture evaluation, "
        "snore detection, and AI sleep insights."
    ),
    version="1.0.0"
)

app.include_router(health.router)
app.include_router(posture.router)
app.include_router(snore.router)