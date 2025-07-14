from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from domain.question import question_router
from domain.answer import answer_router
from domain.user import user_router
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

app = FastAPI()

origins = [
    "http://localhost:5173",    # 또는 "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(question_router.router)
app.include_router(answer_router.router)
app.include_router(user_router.router)
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))