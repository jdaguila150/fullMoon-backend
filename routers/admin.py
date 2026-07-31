from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, security
from security import require_admin
from database import get_db

router = APIRouter(prefix="/api/admin/lessons", tags=["Administración"])

@router.post("/seed")
def seed_lesson_content(
    payload: schemas.LessonContentSeed,
    current_user: models.User = Depends(security.require_admin),
    db: Session = Depends(get_db)
):
    # Opcional en el futuro: Verificar si current_user tiene un rol de 'admin'
    
    # Buscamos si la lección ya existe para actualizarla (Upsert)
    lesson = db.query(models.LessonContent).filter(models.LessonContent.id == payload.id).first()
    
    if lesson:
        lesson.module_id = payload.module_id
        lesson.theory_payload = payload.theory_payload
        lesson.exam_payload = payload.exam_payload
        lesson.prerequisites = payload.prerequisites 
        action = "actualizada"
    else:
        lesson = models.LessonContent(
            id=payload.id,
            module_id=payload.module_id,
            theory_payload=payload.theory_payload,
            exam_payload=payload.exam_payload,
            prerequisites=payload.prerequisites
        )
        db.add(lesson)
        action = "creada"
        
    db.commit()
    
    return {"mensaje": f"Lección {action} con éxito", "lesson_id": lesson.id}