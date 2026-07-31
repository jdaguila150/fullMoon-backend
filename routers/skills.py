from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

# Importa tus dependencias locales (ajusta las rutas según tu proyecto)
from database import get_db
from models import Skill, UserSkill, User
from schemas import SkillUnlockPayload, EquipSkillsPayload
import security

router = APIRouter(prefix="/api/skills", tags=["Arena Skills"])

@router.get("/")
def get_skills(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(security.get_optional_current_user) 
):
    # Traemos todo el catálogo de la tienda
    skills = db.query(Skill).all()

    # Si hay un usuario logueado, traemos su inventario
    user_unlocked_ids = set()
    if current_user:
        # IMPORTANTE: Asegúrate de usar UserSkill.skill_id (como se llama en tu modelo)
        user_skills = db.query(UserSkill.skill_id).filter(UserSkill.user_id == current_user.id).all()
        user_unlocked_ids = {us[0] for us in user_skills}

    result = []
    for skill in skills:
        skill_dict = {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "branch": skill.branch,
            "level": skill.level,
            "energy_cost": skill.energy_cost,
            "prerequisites": skill.prerequisites,
            
            # --- AQUÍ ESTABA EL ERROR ---
            # Leemos los campos correctos de tu modelo original
            "effect_type": skill.effect_type,
            "effect_value": skill.effect_value,
            
            "is_unlocked": skill.id in user_unlocked_ids if current_user else False
        }
        result.append(skill_dict)

    return result

@router.post("/unlock")
def unlock_skill(
    request: SkillUnlockPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    skill_id = request.skill_id

    # 1. Verificamos que el nodo de habilidad realmente exista en el catálogo
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=400, detail="El nodo de habilidad solicitado no existe.")

    # 2. Verificamos que no lo haya comprado antes
    existing_unlock = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill_id
    ).first()
    if existing_unlock:
        raise HTTPException(status_code=400, detail="Ya tienes esta habilidad desbloqueada.")

    # 3. Validamos el balance de energía
    if current_user.energy_balance < skill.energy_cost:
        raise HTTPException(
            status_code=400, 
            detail=f"Energía insuficiente. Cuesta {skill.energy_cost} y tienes {current_user.energy_balance}."
        )

    # 4. Verificamos los prerrequisitos estrictamente
    if skill.prerequisites:
        # Obtenemos los IDs de las habilidades que el usuario YA tiene
        unlocked_skills = db.query(UserSkill.skill_id).filter(UserSkill.user_id == current_user.id).all()
        unlocked_skill_ids = {us[0] for us in unlocked_skills}

        for req_id in skill.prerequisites:
            if req_id not in unlocked_skill_ids:
                raise HTTPException(
                    status_code=400, 
                    detail=f"No puedes desbloquear esto aún. Te falta el prerrequisito: {req_id}"
                )

    # 5. La Transacción (Bloque Try/Except para evitar pérdida de datos o energía fantasma)
    try:
        # Cobramos la energía
        current_user.energy_balance -= skill.energy_cost
        
        # Insertamos en el inventario
        new_user_skill = UserSkill(user_id=current_user.id, skill_id=skill_id)
        db.add(new_user_skill)
        
        # Confirmamos los cambios de ambas tablas al mismo tiempo
        db.commit()
        
        return {
            "success": True, 
            "message": "¡Habilidad desbloqueada con éxito!", 
            "energy_remaining": current_user.energy_balance
        }
        
    except Exception as e:
        db.rollback() # Si algo explota (ej: se cae la BD en ese instante), devolvemos la energía al usuario
        raise HTTPException(status_code=400, detail="Error al procesar el desbloqueo. Intenta nuevamente.")

    



@router.put("/equip")
def equip_user_skills(
    payload: EquipSkillsPayload, 
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    # 1. Validación: Máximo 3 habilidades
    if len(payload.skill_ids) > 3:
        raise HTTPException(status_code=400, detail="Solo puedes equipar un máximo de 3 habilidades.")

    # 2. Desequipar todas las habilidades actuales del usuario
    db.query(UserSkill).filter(UserSkill.user_id == current_user.id).update({"is_equipped": False})

    # 3. Equipar las nuevas (si envió alguna)
    if payload.skill_ids:
        # Buscamos que realmente posea las habilidades que intenta equi par
        owned_skills = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id.in_(payload.skill_ids)
        ).all()

        # Validación: ¿Intentó equipar algo que no ha comprado?
        if len(owned_skills) != len(payload.skill_ids):
            raise HTTPException(status_code=403, detail="Estás intentando equipar habilidades que no posees.")

        # Marcamos como equipadas
        for skill in owned_skills:
            skill.is_equipped = True

    # 4. Guardar cambios
    db.commit()
    
    return {"success": True, "message": "Equipamiento actualizado para la Arena."}




@router.get("/me/skills")
def get_my_skills(
    db: Session = Depends(get_db), 
    current_user: User = Depends(security.get_current_user)
):
    # Hacemos un JOIN entre UserSkill y Skill para traer los datos completos
    resultados = (
        db.query(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .filter(UserSkill.user_id == current_user.id)
        .all()
    )

    habilidades = []
    for user_skill, skill in resultados:
        habilidades.append({
            "id": skill.id,           # El ID real de la habilidad
            "name": skill.name,       # Nombre visual (ej. "Refactorización")
            "is_equipped": user_skill.is_equipped # True/False
        })

    return habilidades