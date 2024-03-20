from . import router

from app.models.user import UserSignUpForm, UserInDB


@router.post("/signup")
async def signup(signup_form: UserSignUpForm):
    user = await UserInDB.async_find_one(username=signup_form.username)
    if (user):
        return {"message": "Username already exists!"}
    user = UserInDB(username=signup_form.username)
    user.set_password(signup_form.password)
    await user.async_save()
    return {"message": "User created!"}
