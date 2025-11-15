from fastapi import FastAPI, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from .config import config
from .webhook import verify_circle_signature

app = FastAPI(title="Circle webhook service")


@app.on_event("startup")
async def startup_event():
    # Access config to ensure it's loaded
    # This will raise on missing required env vars
    _ = config.CIRCLE_API_KEY


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/circle-webhook")
async def circle_webhook(request: Request, x_circle_signature: str | None = Header(None)):
    """
    Expects the Circle signature header (replace header name if Circle uses another).
    Reads raw body to compute HMAC and verify against WEBHOOK_SECRET.
    """
    raw = await request.body()
    if not verify_circle_signature(raw, x_circle_signature, config.WEBHOOK_SECRET):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # Parse JSON payload (already read the body)
    payload = await request.json()
    # TODO: process payload according to your business logic
    return JSONResponse({"received": True, "event": payload.get("type")})
