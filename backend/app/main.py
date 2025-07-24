from fastapi import FastAPI
from app.api import users



app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(users.router)