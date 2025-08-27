# test_acceso.py
import json

print("=== Verificando acceso a datos ===")

# Verificar familias.json
try:
    with open('datos/familias.json', 'r', encoding='utf-8') as f:
        familias_data = json.load(f)
    print("[OK] familias.json cargado correctamente")
    
    total_personas = 0
    for familia_id, familia in familias_data['familias'].items():
        miembros = familia['miembros']
        total_personas += len(miembros)
        print(f"Familia {familia_id}: {familia['nombre']} - {len(miembros)} miembros")
        for miembro in miembros:
            print(f"  - {miembro['cedula']}: {miembro['nombre']}")
    
    print(f"Total de personas en familias.json: {total_personas}")
    
except Exception as e:
    print(f"[ERROR] Error cargando familias.json: {e}")

# Verificar relaciones.json (después de ejecutar inferencia.py)
try:
    with open('relaciones.json', 'r', encoding='utf-8') as f:
        relaciones_data = json.load(f)
    print("\n[OK] relaciones.json cargado correctamente")
    
    personas_relaciones = relaciones_data['relaciones_por_persona']
    print(f"Total de personas en relaciones.json: {len(personas_relaciones)}")
    
    for cedula, datos in personas_relaciones.items():
        print(f"  - {cedula}: {datos['nombre']}")
        
except Exception as e:
    print(f"[ERROR] Error cargando relaciones.json: {e}")
    print("¿Ejecutaste inferencia.py?")