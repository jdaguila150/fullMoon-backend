from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    energy_balance = Column(Integer, default=0)
    role = Column(String, default="user")
    
    progress = relationship("Progress", back_populates="user")
    skills = relationship("UserSkill", back_populates="user")

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(String, nullable=False)
    lesson_id = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    score = Column(Float, default=0.0)

    user = relationship("User", back_populates="progress")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, index=True) # ej: 'extra_time_lvl1'
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # --- NUEVOS CAMPOS PARA EL ÁRBOL (RAMAS, NIVELES Y PRERREQUISITOS) ---
    branch = Column(String, nullable=False, default="general") # ej: 'velocidad', 'precision'
    level = Column(Integer, nullable=False, default=1)
    prerequisites = Column(JSON, default=list) # Lista de IDs requeridos, ej: ["extra_time_lvl1"]
    # ---------------------------------------------------------------------

    energy_cost = Column(Integer, nullable=False)
    effect_type = Column(String, nullable=False)      # ej: 'arena_time_bonus'
    effect_value = Column(Float, nullable=False)
    
    unlocked_by = relationship("UserSkill", back_populates="skill")

class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="unlocked_by")

    is_equipped = Column(Boolean, default=False, nullable=False)

class LessonContent(Base):
    __tablename__ = "lesson_contents"
    
    id = Column(String, primary_key=True, index=True) # Ej: 'fundamentos_01_a'
    module_id = Column(String, index=True, nullable=False) # Ej: 'fundamentos_01'
    theory_payload = Column(JSON, nullable=False)
    exam_payload = Column(JSON, nullable=False)
    prerequisites = Column(JSON, default=list)



# Añade esto en models.py
class ArenaChallenge(Base):
    __tablename__ = "arena_challenges"
    
    id = Column(String, primary_key=True, index=True)
    tipo_reto = Column(String, nullable=False) # 'teorico' o 'algoritmico'

    node_id = Column(String, index=True, nullable=False)
    
    recompensa = Column(Integer, nullable=False, default=25)
    
    # --- Campos para Teoría ---
    pregunta = Column(Text, nullable=True)
    opciones = Column(JSON, nullable=True)
    indice_correcto = Column(Integer, nullable=True)
    
    # --- Campos para Algoritmia ---
    codigo_inicial = Column(Text, nullable=True)
    casos_prueba = Column(JSON, nullable=True)

    tiempo_limite = Column(Integer, nullable=False, default=60)


# Añade esto en models.py
class LearningModule(Base):
    __tablename__ = "learning_modules"
    
    id = Column(String, primary_key=True, index=True) # ej. 'python_01'
    titulo = Column(String, nullable=False)           # ej. 'Python Básico'
    canvas_data = Column(JSON, nullable=True)