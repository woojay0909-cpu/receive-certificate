from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from engine import SignalEngine
import datetime as dt
import uuid

app = FastAPI(title="Receive Certificate - Oracle API")

# CORS for local dev; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENGINE = SignalEngine()  # stateless-ish engine; internal caching possible

class SignalOut(BaseModel):
    id: str
    timestamp: str
    symbol: str
    side: str
    price: float
    confidence: float
    reason: str

# lightweight in-memory store (replace with DB for production)
SIGNAL_STORE: List[SignalOut] = []

@app.get("/signals/latest", response_model=List[SignalOut])
def get_latest(limit: int = 20):
    return SIGNAL_STORE[:limit]

@app.post("/signals/generate", response_model=SignalOut)
def generate_once():
    result = ENGINE.generate_signal_now()
    if not result:
        raise HTTPException(status_code=204, detail="No signal at this time")
    sig = SignalOut(
        id=str(uuid.uuid4()),
        timestamp=dt.datetime.utcnow().isoformat()+"Z",
        symbol=result["symbol"],
        side=result["side"],
        price=float(result["price"]),
        confidence=float(result["confidence"]),
        reason=result.get("reason","")
    )
    # push into store (most recent first)
    SIGNAL_STORE.insert(0, sig)
    # trim store
    while len(SIGNAL_STORE) > 200:
        SIGNAL_STORE.pop()
    return sig

# Optional: endpoint to simulate a schedule runner or allow webhooks to start background process
@app.post("/signals/start_scheduler")
def start_scheduler(background_tasks: BackgroundTasks):
    # In production, run a proper scheduler (cron, Celery beat, or hosted cron)
    # Here we return 202; integrate scheduler externally.
    return {"status":"ok","note":"Run a scheduler externally to call /signals/generate periodically."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)