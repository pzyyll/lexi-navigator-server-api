from libs.pyhelper.singleton import SingletonMeta


class GM(metaclass=SingletonMeta):

    def add_user(self, username, passwd):
        from app.models.user import UserCheck, UserInDB, ValidationError
        try:
            UserCheck(username=username, password=passwd)
        except ValidationError as e:
            return e.errors()
        user = UserInDB(username=username, password=passwd)
        user.save()
