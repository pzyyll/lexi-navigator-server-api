from mongoengine import StringField
from passlib.context import CryptContext


class PasswordField(StringField):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __set__(self, instance, value):
        value = self.generate_hash(value)
        return super().__set__(instance, value)

    def generate_hash(self, passwd):
        return self.pwd_context.hash(passwd)

    def verify(self, passwd):
        return self.pwd_context.verify(passwd, self)
