from . import router
from fastapi import File, UploadFile, Depends
from ..auth.token import get_token_user
from app.models.user import UserInDB


@router.get("/photo-to-text")
async def photo_to_text(
    file: UploadFile = File(...), user: UserInDB = Depends(get_token_user)
):
    content = await file.read()
    # Do something with the content
    print("photo_to_text", content)
    return {"message": "Hello World"}
