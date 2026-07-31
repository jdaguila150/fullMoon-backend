from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, security
from database import get_db
from security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario o email ya está registrado")
        
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        password_hash=hashed_password,
        energy_balance=0
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = security.create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    
    if not user or not security.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        
    access_token = security.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado, incluyendo su balance de energía."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "energy_balance": current_user.energy_balance
    }