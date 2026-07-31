from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional # <--- NUEVO: Importamos Optional
from database import get_db
from models import User

SECRET_KEY = "super_secreto_para_fullmoon_en_produccion_cambiar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# El Cadenero Estricto (Lanza error si no hay token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# NUEVO: El Recepcionista Amable (Devuelve None si no hay token, no lanza error)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False) 

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependencia para proteger rutas (ESTRICTA)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user


# NUEVO: Dependencia para rutas públicas o mixtas (OPCIONAL)
def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    # Si no nos mandaron token, simplemente regresamos None (es un invitado)
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        # Si el token es inválido o no tiene username, también lo tratamos como invitado
        if username is None:
            return None
            
    except JWTError:
        # Si el token expiró o está corrupto, no explotamos, solo regresamos None
        return None
        
    # Si todo salió bien, buscamos al usuario igual que en la función estricta
    user = db.query(User).filter(User.username == username).first()
    
    return user


def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador"
        )
    return current_user