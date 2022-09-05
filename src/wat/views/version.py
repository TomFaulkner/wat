import subprocess

from fastapi import APIRouter

router = APIRouter()


@router.get("/version")
def get_git_revision_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return "Git not installed or no commits exist."


def init_app(app):
    app.include_router(router)
