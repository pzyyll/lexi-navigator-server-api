import uuid
import re

from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, validator
from passlib.context import CryptContext

from mongoengine import StringField, EmailField, DateTimeField, UUIDField, LongField
from app.common.db.fields import PasswordField
from app.common.db.basedoc import BaseDocument


class UserCheck(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=8, max_length=20)

    @validator('password')
    def password_complexity_check(cls, v):
        # 正则表达式检查密码是否包含至少一个数字和一个大写字母
        if not re.findall(r'(?=.*\d)(?=.*[A-Z])', v):
            raise ValueError(
                'Password must contain at least one digit and one uppercase letter'
            )
        return v


class UserSignUpForm(UserCheck):
    invitation_code: str
    # email: str = Field(None, min_length=5, max_length=50)

    # @validator('email')
    # def email_check(cls, v):
    #     if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
    #         raise ValueError('Invalid email address')
    #     return v
    @validator('invitation_code')
    def invitation_code_check(cls, v):
        from app.settings import settings
        invitation_code = settings.signup_secret
        if invitation_code:
            if v != invitation_code:
                raise ValueError('Invalid invitation code')
        return v


class UserInDB(BaseDocument):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    userid = UUIDField(parimary_key=True,
                       required=True,
                       unique=True,
                       default=uuid.uuid4().hex)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = EmailField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    login_token_version = LongField(default=1)
    api_token_version = LongField(default=1)

    meta = {
        "collection": "users",
        "indexes": ["userid", "username"],
    }

    def set_password(self, passwd):
        self.password = self.generate_hash(passwd)

    def generate_hash(self, passwd):
        return self.pwd_context.hash(passwd)

    def verify_passwd(self, passwd):
        return self.pwd_context.verify(passwd, self.password)
