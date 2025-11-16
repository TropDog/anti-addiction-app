from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.sliding_expiration import SlidingExpirationMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title = "Anti-addiction-app")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlidingExpirationMiddleware)
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

