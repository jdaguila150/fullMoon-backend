from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func # <-- Magia para elegir al azar
from database import get_db
from models import ArenaChallenge, User, UserSkill, Skill
from security import get_current_user 
from schemas import ChallengeCreatePayload
from typing import Optional

router = APIRouter(prefix="/api/arena", tags=["Arena"])

@router.get("/matchmake")
def get_random_challenge(
    modo: str, 
    node_id: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if modo not in ['teorico', 'algoritmico']:
        raise HTTPException(status_code=400, detail="Modo de juego inválido")

    # 1. Buscamos UN reto al azar que coincida con el modo
# 1. Iniciamos la consulta base filtrando SOLO por el modo ('teorico' o 'algoritmico')
    # No ejecutamos la consulta aún (no ponemos .first() ni .all())
    query = db.query(ArenaChallenge).filter(ArenaChallenge.tipo_reto == modo)

    # 2. Verificamos si se proporcionó un node_id (Mini-Arena).
    # Si node_id es None (Arena Global), saltamos este paso y NO agregamos el filtro.
    if node_id:
        # Agregamos el filtro del nodo a la consulta base
        query = query.filter(ArenaChallenge.node_id == node_id)

    # 3. Ejecutamos la consulta final (ya sea con uno o dos filtros), 
    # ordenando al azar y tomando el primero.
    reto = query.order_by(func.random()).first()

    if not reto:
        # Ajustamos el mensaje para que sea más genérico
        raise HTTPException(status_code=404, detail="No hay retos disponibles para esta selección.")

    # 2. Traemos las habilidades que el usuario tiene desbloqueadas
    user_skills = db.query(Skill).join(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    
    # Empaquetamos todo (esta parte se mantiene igual)
    return {
        "challenge": {
            "id": reto.id,
            "tipo_reto": reto.tipo_reto,
            "node_id": reto.node_id, # Añadido por si acaso lo necesitas en frontend
            "recompensa": reto.recompensa,
            "pregunta": reto.pregunta,
            "opciones": reto.opciones,
            "indice_correcto": reto.indice_correcto,
            "codigo_inicial": reto.codigo_inicial,
            "casos_prueba": reto.casos_prueba
        },
        "equippedSkills": [
            {"id": s.id, "name": s.name, "effect_code": s.effect_type} for s in user_skills
        ]
    }






# Endpoint para inyectar retos (POST)
@router.post("/admin/challenges")
def create_challenge(payload: ChallengeCreatePayload, db: Session = Depends(get_db)):
    # 1. Verificar si el ID del reto ya existe para evitar colisiones
    existing = db.query(ArenaChallenge).filter(ArenaChallenge.id == payload.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un reto con este ID.")
        
    # 2. Construir el objeto para la BD
    nuevo_reto = ArenaChallenge(
        id=payload.id,
        node_id=payload.node_id,
        tipo_reto=payload.tipo_reto,
        recompensa=payload.recompensa,
        tiempo_limite=payload.tiempo_limite,
        pregunta=payload.pregunta,
        opciones=payload.opciones,
        indice_correcto=payload.indice_correcto,
        codigo_inicial=payload.codigo_inicial,
        casos_prueba=payload.casos_prueba
    )
    
    # 3. Guardar en SQLite/PostgreSQL
    db.add(nuevo_reto)
    db.commit()
    
    return {"success": True, "message": "Reto añadido correctamente a la mini-arena."}



    # 1. Obtener todos los retos de un módulo específico
@router.get("/admin/challenges/{node_id}")
def get_challenges_by_node(node_id: str, db: Session = Depends(get_db)):
    retos = db.query(ArenaChallenge).filter(ArenaChallenge.node_id == node_id).all()
    return retos

# 2. Actualizar un reto existente
@router.put("/admin/challenges/{challenge_id}")
def update_challenge(
    challenge_id: str, 
    payload: ChallengeCreatePayload, 
    db: Session = Depends(get_db)
):
    reto = db.query(ArenaChallenge).filter(ArenaChallenge.id == challenge_id).first()
    
    if not reto:
        raise HTTPException(status_code=404, detail="Reto no encontrado.")
        
    # Actualizamos los campos
    reto.tipo_reto = payload.tipo_reto
    reto.recompensa = payload.recompensa
    reto.tiempo_limite = payload.tiempo_limite
    reto.pregunta = payload.pregunta
    reto.opciones = payload.opciones
    reto.indice_correcto = payload.indice_correcto
    reto.codigo_inicial = payload.codigo_inicial
    reto.casos_prueba = payload.casos_prueba
    
    db.commit()
    return {"success": True, "message": "Reto actualizado correctamente."}