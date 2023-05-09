import logging
from asyncio import sleep
from uuid import UUID, uuid4

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


origins = [
    "http://localhost:5173",
    "http://localhost",
]


def get_app():
    app = FastAPI(title="Dummy")

    return app


app = get_app()


@app.get("/")
async def root():
    return {"message": "Hello World"}


polling_ids = {}


@app.post("/pollable", status_code=202)
async def pollable_post(count: int):
    poll_id = uuid4()
    logger.info("Created pollable with id:%s", poll_id)
    polling_ids[str(poll_id)] = {"polls": 0, "respond_when": count}
    return {"id": poll_id, "polls": 0, "respond_when": count}


@app.get("/pollable/{id_}")
async def pollable_get(id_: UUID):
    try:
        polling_ids[str(id_)]["polls"] += 1
    except KeyError as e:
        raise HTTPException(
            status_code=404, detail=f"No job was found with id:{id_}"
        ) from e
    else:
        response = {
            "id": id_,
            "polls": polling_ids[str(id_)]["polls"],
            "respond_when": polling_ids[str(id_)]["respond_when"],
            "complete": False,
        }
        if polling_ids[str(id_)]["polls"] == polling_ids[str(id_)]["respond_when"]:
            response["complete"] = True
            return response
        elif polling_ids[str(id_)]["polls"] > polling_ids[str(id_)]["respond_when"]:
            raise HTTPException(
                status_code=409, detail=f"Response for id:{id_} was already returned."
            )
        return response


class Callback(BaseModel):
    url: str
    body: dict


class CallbackException(ValueError):
    """Remote API returned a non-200 status code."""

    def __init__(self, code, body):
        super().__init__(f"Response was other than 200: {code}\n{body}")


async def do_callback(cb: Callback):
    await sleep(5)
    async with httpx.AsyncClient() as client:
        r = await client.post(cb.url, json=cb.body)
        if not r.status_code == 200:
            raise CallbackException(r.status_code, r.json())


@app.post("/callback", status_code=202)
async def callback_post(cb: Callback, bg: BackgroundTasks, updates=0, delay=0):
    cb_id = uuid4()
    logger.info("Created callback with id:%s", cb_id)
    cb.body["complete"] = False
    bg.add_task(do_callback, cb)
    cb2 = Callback(**cb.dict())
    cb2.body["complete"] = True
    bg.add_task(do_callback, cb2)
    return {"id": cb_id, "updates": updates, "delay": delay}


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
