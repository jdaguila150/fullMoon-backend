import json
from database import SessionLocal
from models import ArenaChallenge

def seed_challenges():
    try:
        with open('retos.json', 'r', encoding='utf-8') as f:
            retos_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'retos.json'")
        return

    db = SessionLocal()
    
    try:
        for item in retos_data:
            existing = db.query(ArenaChallenge).filter(ArenaChallenge.id == item['id']).first()
            
            if existing:
                existing.tipo_reto = item['tipo_reto']
                existing.recompensa = item.get('recompensa', 25)
                existing.pregunta = item.get('pregunta')
                existing.opciones = item.get('opciones')
                existing.indice_correcto = item.get('indice_correcto')
                existing.codigo_inicial = item.get('codigo_inicial')
                existing.casos_prueba = item.get('casos_prueba')
                print(f"🔄 Actualizado: {item['id']}")
            else:
                new_challenge = ArenaChallenge(
                    id=item['id'],
                    tipo_reto=item['tipo_reto'],
                    recompensa=item.get('recompensa', 25),
                    pregunta=item.get('pregunta'),
                    opciones=item.get('opciones'),
                    indice_correcto=item.get('indice_correcto'),
                    codigo_inicial=item.get('codigo_inicial'),
                    casos_prueba=item.get('casos_prueba')
                )
                db.add(new_challenge)
                print(f"✅ Creado: {item['id']}")
        
        db.commit()
        print(f"\n🎉 ¡Listo! Se inyectaron {len(retos_data)} retos en la Arena.")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_challenges()