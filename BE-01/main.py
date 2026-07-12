from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FlyRank!"}

@app.get("/status")
def read_status():
    return {"status": "ok", "service": "BE-01"}