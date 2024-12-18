from fastapi import FastAPI, FastAPI, HTTPException, Depends, status,Security,Form
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from auth import *
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel
from settings import *
from models import User1,LoginHistory
from passlib.context import CryptContext
import jwt
from datetime import timedelta
from tortoise.exceptions import DoesNotExist
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist
import redis
app=FastAPI()
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login_with_username",description="OAuth2 Password Bearer")

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,

)
class RefreshToken(BaseModel):
    refresh_token: str
class LoginUser_email(BaseModel):
    email: str
    password: str
class LoginUser_username(BaseModel):
    username: str
    password: str
class UpdateUser(BaseModel):
    email: str | None = None
    password: str | None = None
class RegisterUser(BaseModel):
    email: str
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 验证访问令牌并获取用户ID
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        # 获取用户实例
        user_obj = await User1.get(email=email)
        
        return user_obj
    except jwt.PyJWTError:
        raise credentials_exception


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: RegisterUser):
    # 检查电子邮件是否已经注册
    try:
        # 使用get方法来检查用户是否存在，如果不存在则抛出DoesNotExist异常
        await User1.get(email=user.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    except DoesNotExist:
        # 如果用户不存在，继续创建新用户
        pass
    
    # 创建新用户
    hashed_password = pwd_context.hash(user.password)
    new_user = await User1.create(email=user.email, username=user.email, hashed_password=hashed_password)
    
    return {"message": "User created successfully"}


@app.post("/login_with_email", status_code=status.HTTP_200_OK)
async def login(user: LoginUser_email):
    # 检查电子邮件和密码
    try:
        user_obj = await User1.get(email=user.email)
    except User1.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    # 验证密码
    if not user_obj.check_password(user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    # 创建访问和刷新令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_obj.email}, expires_delta=access_token_expires)
    
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(data={"sub": user_obj.email}, expires_delta=refresh_token_expires)
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post("/login_with_username", status_code=status.HTTP_200_OK)
async def login_with_username(
    username: str = Form(...), 
    password: str = Form(...),
):
    # 检查用户名和密码
    try:
        user_obj = await User1.get(username=username)
    except User1.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    # 验证密码
    if not user_obj.check_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    # 创建访问和刷新令牌
    access_token_expires = timedelta(minutes=30)  # 假设您的 ACCESS_TOKEN_EXPIRE_MINUTES 是 30
    access_token = create_access_token(data={"sub": user_obj.email}, expires_delta=access_token_expires)
    
    refresh_token_expires = timedelta(minutes=60 * 24 * 7)  # 假设您的 REFRESH_TOKEN_EXPIRE_MINUTES 是 60 * 24 * 7
    refresh_token = create_refresh_token(data={"sub": user_obj.email}, expires_delta=refresh_token_expires)
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post("/refresh")
async def refresh_token(refresh: RefreshToken):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码刷新令牌以获取用户信息
        payload = verify_refresh_token(refresh.refresh_token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        # 如果刷新令牌无效或过期，返回错误
        raise e    
    
@app.put("/user/update", status_code=status.HTTP_200_OK)
async def update_user(user: UpdateUser, current_user: User1 = Depends(get_current_user)):
    if user.email:
        current_user.email = user.email
    if user.password:
        current_user.set_password(user.password)
    await current_user.save()
    return {"message": "User updated successfully"}




@app.get("/user/history", status_code=status.HTTP_200_OK)
async def user_history(current_user: User1 = Depends(get_current_user)):
    history = await LoginHistory.filter(user=current_user).all()
    history_data = [{"user_agent": item.user_agent, "timestamp": item.timestamp.isoformat()} for item in history]
    return history_data
if __name__=='__main__':
     uvicorn.run("main:app",host='127.0.0.1',port=8080,reload=True,workers=1)

@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: User1 = Depends(get_current_user)):
    refresh_token = "some_logic_to_get_refresh_token_from_db_or_cache"
    redis_client.delete(refresh_token)
    return {"message": "Logged out successfully"}