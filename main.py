from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, lessons, skills, admin, arena, modulos

# Crear tablas en SQLite si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FullMoon API", version="1.0.0")

# Habilitar CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambiar a la URL de tu frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas modulares
app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(skills.router)
app.include_router(admin.router)
app.include_router(arena.router)
app.include_router(modulos.router)