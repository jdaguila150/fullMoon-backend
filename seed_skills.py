import json
from database import SessionLocal
from models import Skill

def seed_skills():
    # 1. Leemos el archivo JSON (asegúrate de que la ruta sea correcta)
    try:
        with open('skills.json', 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'skills.json'")
        return

    db = SessionLocal()
    
    try:
        # 2. Iteramos sobre cada habilidad del JSON
        for item in skills_data:
            # Buscamos si la habilidad ya existe en la BD por su ID
            existing_skill = db.query(Skill).filter(Skill.id == item['id']).first()
            
            if existing_skill:
                # Si existe, ACTUALIZAMOS los valores (por si cambiaste un costo o texto)
                existing_skill.name = item['name']
                existing_skill.description = item['description']
                existing_skill.branch = item.get('branch', 'general')
                existing_skill.level = item.get('level', 1)
                existing_skill.prerequisites = item.get('prerequisites', [])
                existing_skill.energy_cost = item['energy_cost']
                existing_skill.effect_type = item['effect_type']
                existing_skill.effect_value = item['effect_value']
                print(f"🔄 Actualizada: {item['id']}")
            else:
                # Si no existe, CREAMOS una nueva
                new_skill = Skill(
                    id=item['id'],
                    name=item['name'],
                    description=item['description'],
                    branch=item.get('branch', 'general'),
                    level=item.get('level', 1),
                    prerequisites=item.get('prerequisites', []),
                    energy_cost=item['energy_cost'],
                    effect_type=item['effect_type'],
                    effect_value=item['effect_value']
                )
                db.add(new_skill)
                print(f"✅ Creada: {item['id']}")
        
        # 3. Guardamos los cambios en la Base de Datos
        db.commit()
        print(f"\n🎉 ¡Proceso completado! Se procesaron {len(skills_data)} habilidades.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la inyección de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_skills()