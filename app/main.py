from fastapi import FastAPI

app = FastAPI(title="LINEAGE API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
