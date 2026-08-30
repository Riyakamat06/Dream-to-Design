from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth

app = FastAPI()

# CORS setup — without this, the frontend (running on a different
# port/origin) would have every API call silently blocked by the
# browser, even though the backend itself works fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Dream to Design backend is running"}