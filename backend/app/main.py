from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.sliding_expiration import SlidingExpirationMiddleware


app = FastAPI(title = "Anti-addiction-app")

app.add_middleware(SlidingExpirationMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router)