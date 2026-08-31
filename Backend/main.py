from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, milestones
from routers import dreams

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(milestones.router)
app.include_router(dreams.router)


@app.get("/")
def read_root():
    return {"message": "Dream to Design backend is running"}