from fastapi import FastAPI
from app.api import users
from app.core.sliding_expiration import SlidingExpirationMiddleware


app = FastAPI()

app.add_middleware(SlidingExpirationMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(users.router)