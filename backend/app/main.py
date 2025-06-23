from fastapi import FastAPI
from app.api.test_user import router as user_router

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(user_router)