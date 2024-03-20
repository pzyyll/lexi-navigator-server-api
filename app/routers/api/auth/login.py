from . import router

from app.models.user import UserLoginForm, UserInDB


@router.post("/login")
async def login(login_form: UserLoginForm):
    user: UserInDB = await UserInDB.async_find_one(username=login_form.username)
    if (not user.verify_passwd(login_form.password)):
        return {"message": "Invalid password!"}
    if (not user):
        return {"message": "Invalid username!"}
    return {"token": "User logged in!"}
