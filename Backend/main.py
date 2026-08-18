from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Dream to Design backend is running"}