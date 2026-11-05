from dotenv import load_dotenv

load_dotenv()  # noqa: E402 - must run before other app imports read os.environ

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.domain.errors import NotFoundError, ValidationError, ConflictError
from app.api import problems, attempts, evaluations

app = FastAPI(title="LLD Practice Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc), **exc.details})


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


app.include_router(problems.router)
app.include_router(attempts.router)
app.include_router(evaluations.router)


@app.get("/health")
def health():
    return {"status": "ok"}
