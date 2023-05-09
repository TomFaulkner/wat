import logging
from importlib.metadata import entry_points

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_pool

logging.basicConfig(
    format="%(levelname)s: %(module)s:%(lineno)d: %(message)s", level=settings.log_level
)
logger = logging.getLogger(__name__)


origins = [
    "http://localhost:5173",
    "http://localhost",
]


def load_modules(app=None):
    for ep in entry_points()["wat.modules"]:
        logger.info("Loading module: %s", ep.name)
        mod = ep.load()
        if app and (init_app := getattr(mod, "init_app", None)):
            init_app(app)


def get_app():
    app = FastAPI(title="Wat")
    load_modules(app)

    return app


app = get_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    await create_pool()
