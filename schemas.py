from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class LessonCompletePayload(BaseModel):
    module_id: str
    lesson_id: str
    score: float

class SkillUnlockPayload(BaseModel):
    skill_id: str

class LessonContentSeed(BaseModel):
    id: str
    module_id: str
    theory_payload: Dict[str, Any]
    exam_payload: Dict[str, Any]
    prerequisites: List[str] = []


# El esquema de lo que el frontend de admin va a enviar
class ChallengeCreatePayload(BaseModel):
    id: str
    node_id: str
    tipo_reto: str
    recompensa: int
    tiempo_limite: int
    pregunta: Optional[str] = None
    opciones: Optional[List[str]] = None
    indice_correcto: Optional[int] = None
    codigo_inicial: Optional[str] = None
    casos_prueba: Optional[List[dict]] = None


class EquipSkillsPayload(BaseModel):
    skill_ids: List[str]