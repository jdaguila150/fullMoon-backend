from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import LearningModule
# from security import require_admin  <-- Activa esto si proteges tus rutas de admin

router = APIRouter(prefix="/api/modulos", tags=["Modulos"])

# Esquema de validación para recibir los datos de React
class ModuloCreatePayload(BaseModel):
    id: str
    titulo: str

@router.post("/")
def create_modulo(
    payload: ModuloCreatePayload, 
    db: Session = Depends(get_db)
    # current_admin = Depends(require_admin) <-- Descomenta para seguridad
):
    # 1. Verificamos que el ID no exista ya para evitar errores de duplicidad
    existing_mod = db.query(LearningModule).filter(LearningModule.id == payload.id).first()
    if existing_mod:
        raise HTTPException(status_code=400, detail=f"El módulo con ID '{payload.id}' ya existe.")

    # 2. Creamos el nuevo registro
    nuevo_modulo = LearningModule(
        id=payload.id,
        titulo=payload.titulo
    )
    
    # 3. Lo guardamos en la base de datos
    db.add(nuevo_modulo)
    db.commit()
    db.refresh(nuevo_modulo)
    
    # 4. Devolvemos éxito al frontend
    return {
        "success": True, 
        "message": "Módulo creado exitosamente",
        "modulo": {
            "id": nuevo_modulo.id,
            "titulo": nuevo_modulo.titulo
        }
    }

# Ya que estamos aquí, te dejo el GET para que el Dropdown de tu Builder cargue los módulos
@router.get("/")
def get_modulos(db: Session = Depends(get_db)):
    modulos = db.query(LearningModule).all()
    return [{"id": m.id, "titulo": m.titulo} for m in modulos]