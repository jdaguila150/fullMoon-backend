from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, security
from database import get_db
from security import get_current_user

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario o email ya está registrado")
        
    hashed_password = security.get_password_hash(user.password[:72])    
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # Buscamos al usuario en la BD
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    # Truncamos antes de verificar
    safe_password = form_data.password[:72]
    
    if not security.verify_password(safe_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
        
    # Generar y devolver el token...
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,        # <-- MANDAMOS EL ROL AL FRONTEND
        "username": user.username # <-- También útil para mostrar un "Hola, sysadmin_01"
    }



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