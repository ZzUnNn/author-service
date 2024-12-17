from tortoise.models import Model
from tortoise import fields
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User1(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    id_number = fields.CharField(max_length=255, null=True)  # 身份证号码
    username=fields.CharField(max_length=255)
    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

class LoginHistory(Model):
    user = fields.ForeignKeyField('models.User1', related_name='login_history')
    user_agent = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField(auto_now_add=True)
    email = fields.CharField(max_length=255)
    
