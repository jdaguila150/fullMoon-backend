from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, security
from database import get_db

router = APIRouter(prefix="/api/lessons", tags=["Lecciones"])

@router.post("/complete")
def complete_lesson(
    payload: schemas.LessonCompletePayload, 
    current_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db)
):
    is_completed = payload.score >= 70
    energia_ganada = 0
    
    if is_completed:
        if payload.score == 100: energia_ganada = 3
        elif payload.score >= 86: energia_ganada = 2
        else: energia_ganada = 1

    progreso = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.lesson_id == payload.lesson_id
    ).first()

    if progreso:
        if payload.score > progreso.score:
            progreso.score = payload.score
        
        if not progreso.is_completed and is_completed:
            progreso.is_completed = True
            current_user.energy_balance += energia_ganada
    else:
        nuevo_progreso = models.Progress(
            user_id=current_user.id,
            module_id=payload.module_id,
            lesson_id=payload.lesson_id,
            is_completed=is_completed,
            score=payload.score
        )
        db.add(nuevo_progreso)
        
        if is_completed:
            current_user.energy_balance += energia_ganada

    db.commit()
    db.refresh(current_user)

    return {
        "aprobado": is_completed,
        "score": payload.score,
        "energia_ganada": energia_ganada if (not progreso or not progreso.is_completed) else 0,
        "balance_energia_total": current_user.energy_balance
    }


@router.get("/modules")
def get_all_modules(
    current_user: models.User = Depends(security.get_current_user), # Opcional, si quieres protegerlo
    db: Session = Depends(get_db)
):
    # 1. Buscamos todos los module_id de la tabla y usamos .distinct() para no traer repetidos
    modulos_unicos = db.query(models.LessonContent.module_id).distinct().all()
    
    # SQLAlchemy devuelve una lista de tuplas: [("mod-01",), ("fundamentos_01",)]
    # 2. Lo formateamos como una lista de diccionarios para que el frontend lo entienda
    resultado = [{"id": m[0], "titulo": m[0]} for m in modulos_unicos]
    
    return resultado




@router.get("/tree/{module_id}")
def get_learning_tree(
    module_id: str, 
    current_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. Obtener todas las lecciones
    lessons = db.query(models.LessonContent).filter(models.LessonContent.module_id == module_id).all()
    
    # 2. Obtener el progreso del usuario
    user_progress = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.is_completed == True
    ).all()
    completed_lesson_ids = {p.lesson_id for p in user_progress}
    
    tree_nodes = []
    
    for lesson in lessons:
        status = "locked"
        
        # Validar si ya está completada
        if lesson.id in completed_lesson_ids:
            status = "completed"
        else:
            prereqs = lesson.prerequisites or []
            if all(req in completed_lesson_ids for req in prereqs):
                status = "active"
                
        # Protegemos contra payloads nulos
        th_payload = lesson.theory_payload or {}
        ex_payload = lesson.exam_payload or {}
        
        # Extraemos absolutamente todo para el CMS
        tree_nodes.append({
            "id": lesson.id,
            "titulo": th_payload.get("titulo", f"Lección {lesson.id}"),
            "prerequisites": lesson.prerequisites or [],
            "status": status,
            "nodeType": th_payload.get("gamificacion", {}).get("rama_arbol", "primary"),
            
            # --- DATOS EXTRA PARA EL CREADOR VISUAL (CMS) ---
            "teoria_markdown": th_payload.get("teoria_markdown", ""),
            "instrucciones": th_payload.get("instrucciones", ""),
            "lenguaje": th_payload.get("lenguaje", "python"),
            "codigo_inicial": th_payload.get("codigo_inicial", ""),
            "preguntas": ex_payload.get("preguntas", [])
        })
        
    return {"nodes": tree_nodes}






@router.get("/{lesson_id}")
def get_lesson_content(lesson_id: str, db: Session = Depends(get_db)):
    lesson = db.query(models.LessonContent).filter(models.LessonContent.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lección no encontrada"
        )
        
    # FastAPI serializa automáticamente la columna JSON de SQLAlchemy a JSON real en la respuesta
    return {
        "id": lesson.id,
        "module_id": lesson.module_id,
        "theory_payload": lesson.theory_payload,
        "exam_payload": lesson.exam_payload
    }
