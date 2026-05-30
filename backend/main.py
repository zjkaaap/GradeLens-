from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI 试卷评分", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "model": settings.MODEL_NAME}


from routers import paper as paper_router  # noqa: E402
from routers import grade as grade_router  # noqa: E402

app.include_router(paper_router.router, prefix="/api/paper", tags=["paper"])
app.include_router(grade_router.router, prefix="/api", tags=["grade"])
