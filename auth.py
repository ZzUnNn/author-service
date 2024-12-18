import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from settings import *


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 函数：创建刷新令牌
def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
def verify_token(token: str, credentials_exception):
    try:
        # 尝试解码 JWT 令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 从解码后的 payload 中获取用户 ID
        email = payload.get("email")
        
        # 如果 user_id 不存在，说明令牌不包含必要的信息，抛出异常
        if email is None:
            raise credentials_exception
        
        # 如果令牌验证通过，返回用户 ID
        return email
    
    except jwt.PyJWTError:
        # 如果令牌无效或过期，抛出 401 未授权异常
        raise credentials_exception