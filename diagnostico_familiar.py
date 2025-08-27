# diagnostico_familiar.py
import json
from datetime import datetime


def cargar_personas(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)


def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return None
    try:
        nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.now()
        return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    except:
        return None


def diagnosticar_familia():
    personas = cargar_personas('personas.json')

    # Agregar edades
    for p in personas:
        p['edad'] = calcular_edad(p['fecha_nacimiento'])

    print("=== DIAGNÓSTICO FAMILIAR ===")
    print("Personas ordenadas por edad (de mayor a menor):")

    personas_ordenadas = sorted(personas, key=lambda x: x['edad'] if x['edad'] else 0, reverse=True)

    for i, p in enumerate(personas_ordenadas):
        print(f"{i + 1}. {p['nombre']} {p['apellido1']} {p['apellido2']}")
        print(f"   Cédula: {p['cedula']}")
        print(f"   Fecha nac: {p['fecha_nacimiento']} (Edad: {p['edad']})")
        print(f"   Estado civil: {p['estado_civil']}")
        print()

    print("=== ANÁLISIS DE POSIBLES RELACIONES ===")

    # Agrupar por apellidos
    from collections import defaultdict
    apellidos_paternos = defaultdict(list)
    apellidos_maternos = defaultdict(list)

    for p in personas:
        if p['apellido1']:
            apellidos_paternos[p['apellido1']].append(p)
        if p['apellido2']:
            apellidos_maternos[p['apellido2']].append(p)

    print("Familias por apellido paterno:")
    for apellido, personas_grupo in apellidos_paternos.items():
        if len(personas_grupo) > 1:
            print(f"  {apellido}: {[p['nombre'] for p in personas_grupo]}")

    print("\nFamilias por apellido materno:")
    for apellido, personas_grupo in apellidos_maternos.items():
        if len(personas_grupo) > 1:
            print(f"  {apellido}: {[p['nombre'] for p in personas_grupo]}")


if __name__ == "__main__":
    diagnosticar_familia()