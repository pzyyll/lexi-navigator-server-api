from . import router
from fastapi import Request, Depends


@router.api_route("/completion", methods=["GET", "POST"])
async def completion(request: Request):
    return {"message": "This is the completion route in the chat router!"}
