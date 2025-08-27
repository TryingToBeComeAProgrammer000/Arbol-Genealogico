# inferencia_desde_cero.py
"""
Sistema para inferir relaciones familiares desde cero.
Carga datos de personas y matrimonios, infiere relaciones y guarda el resultado.
"""

import json
import logging
from datetime import datetime
from collections import defaultdict

# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PARENT_MIN_AGE_DIFF = 13
PARENT_MAX_AGE_DIFF = 60
TYPICAL_PARENT_AGE = 28


# --- Funciones de Carga y Guardado ---
def cargar_personas_desde_personas_json(archivo="personas.json"):
    """Carga personas desde personas.json, incluyendo todos los datos personales."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("personas.json debe contener una lista de personas")
        personas_dict = {}
        for persona in data:
            cedula = str(persona.get("cedula", "")).strip()
            if not cedula:
                continue
            # Construir nombre completo correctamente
            nombre = persona.get("nombre", "").strip()
            apellido1 = persona.get("apellido1", "").strip()
            apellido2 = persona.get("apellido2", "").strip()
            nombre_completo = f"{nombre} {apellido1} {apellido2}".strip()

            # Añadir edad
            edad = calcular_edad(persona.get("fecha_nacimiento"))

            # Guardar todos los campos
            personas_dict[cedula] = {
                "cedula": cedula,
                "nombre": nombre,
                "apellido1": apellido1,
                "apellido2": apellido2,
                "nombre_completo": nombre_completo,
                "fecha_nacimiento": persona.get("fecha_nacimiento", ""),
                "fecha_fallecimiento": persona.get("fecha_fallecimiento", None),
                "genero": persona.get("genero", "No especificado"),
                "lugar_residencia": persona.get("lugar_residencia", "No especificado"),
                "estado_civil": persona.get("estado_civil", "No especificado"),
                "edad": edad
            }
        logger.info(f"Personas cargadas desde {archivo}: {len(personas_dict)}")
        return personas_dict
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo {archivo}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar {archivo}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error inesperado al cargar personas: {e}")
        return {}


def cargar_matrimonios(archivo="matrimonios.json"):
    """Carga matrimonios desde un archivo JSON."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error("El archivo de matrimonios debe contener una lista")
                return []
            logger.info(f"Matrimonios cargados: {len(data)}")
            return data
    except FileNotFoundError:
        logger.info("Archivo de matrimonios no encontrado")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {archivo}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error al cargar matrimonios: {e}")
        return []


def guardar_relaciones(relaciones_data, archivo="relaciones.json"):
    """Guarda las relaciones inferidas en un archivo JSON."""
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(relaciones_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Relaciones guardadas en {archivo}")
    except Exception as e:
        logger.error(f"Error al guardar relaciones: {e}")


# --- Utilidades ---
def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento."""
    if not fecha_nacimiento or not isinstance(fecha_nacimiento, str):
        return None
    try:
        nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return edad if edad >= 0 else None
    except ValueError:
        return None


def apellidos_set(persona):
    """Devuelve un set con los apellidos en minúscula y sin espacios."""
    s = set()
    if not isinstance(persona, dict):
        return s
    a1 = str(persona.get('apellido1', '')).strip().lower()
    a2 = str(persona.get('apellido2', '')).strip().lower()
    if a1:
        s.add(a1)
    if a2:
        s.add(a2)
    return s


def uniq(seq):
    """Mantiene orden y quita duplicados."""
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


# --- Funciones de Inferencia de Relaciones ---
def construir_parejas(matrimonios):
    """Construye un diccionario de parejas a partir de los matrimonios registrados."""
    parejas = {}  # {cedula: cedula_pareja}
    for matrimonio in matrimonios:
        if isinstance(matrimonio, dict):
            c1 = str(matrimonio.get('conyuge1_cedula', '')).strip()
            c2 = str(matrimonio.get('conyuge2_cedula', '')).strip()
            if c1 and c2:
                parejas[c1] = c2
                parejas[c2] = c1
    logger.info(f"Parejas registradas: {len(parejas)//2} matrimonios")
    return parejas


def _score_parent_candidate(child_age, child_surnames, adult_age, adult_surnames):
    if not isinstance(adult_age, int):
        return -1
    gap = adult_age - (child_age if isinstance(child_age, int) else 0)
    if isinstance(child_age, int):
        if gap < PARENT_MIN_AGE_DIFF or gap > PARENT_MAX_AGE_DIFF:
            return -1
    overlap = len(child_surnames & adult_surnames)
    score = overlap * 10
    if isinstance(child_age, int):
        # bonificación por cercanía a edad típica
        score += max(0, 10 - abs(gap - TYPICAL_PARENT_AGE))
    return score


def inferir_padres_hijos(personas_dict, parejas):
    """
    Infiere relaciones padre-hijo con reglas más estrictas para reducir falsos positivos.
    """
    relaciones = defaultdict(lambda: {'padres': [], 'hijos': []})
    # Asegurar que todos existan en el dict
    for c in personas_dict:
        _ = relaciones[c]

    for cedula_hijo, datos_hijo in personas_dict.items():
        edad_hijo = datos_hijo.get('edad')
        apellidos_hijo = apellidos_set(datos_hijo)
        if not apellidos_hijo:
            continue

        # Candidatos individuales
        candidatos = []
        for cedula_adulto, datos_adulto in personas_dict.items():
            if cedula_adulto == cedula_hijo:
                continue
            if parejas.get(cedula_hijo) == cedula_adulto:
                continue  # jamás pareja

            edad_adulto = datos_adulto.get('edad')
            apellidos_adulto = apellidos_set(datos_adulto)
            s = _score_parent_candidate(edad_hijo, apellidos_hijo, edad_adulto, apellidos_adulto)
            if s >= 0 and len(apellidos_hijo & apellidos_adulto) >= 1:
                candidatos.append((s, cedula_adulto))

        candidatos.sort(reverse=True)

        # Intentar emparejar una pareja registrada
        mejor_par = None
        mejor_par_score = -1
        candidatos_set = {c for _, c in candidatos}
        for _, c1 in candidatos:
            c2 = parejas.get(c1)
            if not c2 or c2 not in candidatos_set or c1 == c2:
                continue
            ap1 = apellidos_set(personas_dict[c1])
            ap2 = apellidos_set(personas_dict[c2])
            union_ap = ap1 | ap2
            if not apellidos_hijo.issubset(union_ap):
                continue
            s1 = _score_parent_candidate(edad_hijo, apellidos_hijo, personas_dict[c1].get('edad'), ap1)
            s2 = _score_parent_candidate(edad_hijo, apellidos_hijo, personas_dict[c2].get('edad'), ap2)
            s_total = s1 + s2
            if s_total > mejor_par_score:
                mejor_par_score = s_total
                mejor_par = (c1, c2)

        padres_asignados = []
        if mejor_par:
            p1, p2 = mejor_par
            padres_asignados = uniq([p1, p2])
        elif candidatos:
            padres_asignados = [candidatos[0][1]]

        # Registrar relaciones
        for p in padres_asignados[:2]:
            if p not in relaciones[cedula_hijo]['padres']:
                relaciones[cedula_hijo]['padres'].append(p)
            if cedula_hijo not in relaciones[p]['hijos']:
                relaciones[p]['hijos'].append(cedula_hijo)

    logger.info("Relaciones padre-hijo inferidas.")
    return relaciones


def hermanos_de(relaciones, cedula_persona):
    """Hermanos: comparten al menos un padre con la persona."""
    hermanxs = set()
    for p in relaciones[cedula_persona]['padres']:
        for h in relaciones[p]['hijos']:
            if h != cedula_persona:
                hermanxs.add(h)
    return list(hermanxs)


def calcular_generaciones(personas_dict, relaciones):
    """Calcula la generación de cada persona usando BFS desde personas sin padres (máx 4)."""
    generaciones = defaultdict(lambda: 1)
    raices = [c for c in personas_dict if not relaciones[c]['padres']]
    for r in raices:
        generaciones[r] = 1

    from collections import deque
    q = deque([(r, 1) for r in raices])
    visitados = set(raices)
    while q:
        actual, gen = q.popleft()
        if gen >= 4:
            continue
        for hijo in relaciones[actual]['hijos']:
            if generaciones[hijo] < gen + 1:
                generaciones[hijo] = gen + 1
            if hijo not in visitados:
                visitados.add(hijo)
                q.append((hijo, gen + 1))

    for c in generaciones:
        if generaciones[c] > 4:
            generaciones[c] = 4

    return generaciones


def construir_relaciones_completas(personas_dict, matrimonios, relaciones, generaciones):
    """Construye el diccionario final de relaciones por persona."""
    parejas = construir_parejas(matrimonios)
    relaciones_finales = {}

    for cedula, datos_persona in personas_dict.items():
        # Usar nombre completo ya procesado
        nombre_completo = datos_persona["nombre_completo"]

        padres = uniq(relaciones[cedula]['padres'])
        hijos = uniq(relaciones[cedula]['hijos'])
        pareja = parejas.get(cedula)

        hermanos = uniq(hermanos_de(relaciones, cedula))

        abuelos = []
        for p in padres:
            abuelos.extend(relaciones[p]['padres'])
        abuelos = uniq([a for a in abuelos if a not in padres])

        nietos = []
        for h in hijos:
            nietos.extend(relaciones[h]['hijos'])
        nietos = uniq(nietos)

        tios = []
        for p in padres:
            tios.extend([h for h in hermanos_de(relaciones, p) if h not in padres])
        tios = uniq(tios)

        sobrinos = []
        for h in hermanos:
            sobrinos.extend(relaciones[h]['hijos'])
        sobrinos = uniq(sobrinos)

        primos = []
        for t in tios:
            primos.extend(relaciones[t]['hijos'])
        primos = uniq([p for p in primos if p != cedula and p not in hermanos])

        bisabuelos = []
        for a in abuelos:
            bisabuelos.extend(relaciones[a]['padres'])
        bisabuelos = uniq(bisabuelos)

        bisnietos = []
        for n in nietos:
            bisnietos.extend(relaciones[n]['hijos'])
        bisnietos = uniq(bisnietos)

        sobrinos_nietos = []
        for s in sobrinos:
            sobrinos_nietos.extend(relaciones[s]['hijos'])
        sobrinos_nietos = uniq(sobrinos_nietos)

        tios_abuelos = []
        for a in abuelos:
            tios_abuelos.extend(hermanos_de(relaciones, a))
        tios_abuelos = uniq(tios_abuelos)

        primos_hermanos = primos[:]
        primos_politicos = []
        for pr in primos:
            cony = parejas.get(pr)
            if cony:
                primos_politicos.append(cony)
        if pareja:
            padres_cony = relaciones[pareja]['padres']
            tios_cony = []
            for pc in padres_cony:
                tios_cony.extend([h for h in hermanos_de(relaciones, pc) if h not in padres_cony])
            primos_cony = []
            for tc in uniq(tios_cony):
                primos_cony.extend(relaciones[tc]['hijos'])
            primos_politicos.extend(primos_cony)
        primos_politicos = uniq([x for x in primos_politicos if x not in primos and x != cedula])

        relaciones_finales[cedula] = {
            "nombre": nombre_completo,
            # === Datos personales completos ===
            "fecha_nacimiento": datos_persona.get("fecha_nacimiento", ""),
            "fecha_fallecimiento": datos_persona.get("fecha_fallecimiento", None),
            "genero": datos_persona.get("genero", "No especificado"),
            "lugar_residencia": datos_persona.get("lugar_residencia", "No especificado"),
            "estado_civil": datos_persona.get("estado_civil", "No especificado"),
            # === Relaciones ===
            "relaciones": {
                "padres": padres,
                "hijos": hijos,
                "pareja": pareja,
                "hermanos": hermanos,
                "abuelos": abuelos,
                "nietos": nietos,
                "tios": tios,
                "sobrinos": sobrinos,
                "primos": primos,
                "primos_segundos": [],
                "bisabuelos": bisabuelos,
                "bisnietos": bisnietos,
                "sobrinos_nietos": sobrinos_nietos,
                "tios_abuelos": tios_abuelos,
                "primos_hermanos": primos_hermanos,
                "primos_politicos": primos_politicos,
                "generacion": generaciones.get(cedula, 3)
            }
        }

    return relaciones_finales


# --- Función Principal ---
def main():
    """Función principal para ejecutar la inferencia."""
    logger.info("--- Iniciando Inferencia Familiar ---")

    # 1. Cargar datos desde personas.json (fuente completa)
    personas_dict = cargar_personas_desde_personas_json()
    matrimonios = cargar_matrimonios("matrimonios.json")

    if not personas_dict:
        logger.error("No se pudieron cargar las personas. Finalizando.")
        return

    # 2. Construir parejas registradas
    parejas = construir_parejas(matrimonios)

    # 3. Inferir relaciones padre-hijo
    relaciones_temp = inferir_padres_hijos(personas_dict, parejas)

    # 4. Calcular generaciones
    generaciones = calcular_generaciones(personas_dict, relaciones_temp)

    # 5. Construir relaciones completas
    relaciones_completas = construir_relaciones_completas(
        personas_dict, matrimonios, relaciones_temp, generaciones
    )

    # 6. Preparar datos para guardar
    data_to_save = {
        "ultima_actualizacion": datetime.now().isoformat(),
        "relaciones_por_persona": relaciones_completas
    }

    # 7. Guardar en archivo
    guardar_relaciones(data_to_save, "relaciones.json")

    logger.info("--- Inferencia Familiar Finalizada ---")


if __name__ == "__main__":
    main()# inferencia_desde_cero.py
"""
Sistema para inferir relaciones familiares desde cero.
Carga datos de personas y matrimonios, infiere relaciones y guarda el resultado.
"""

import json
import logging
from datetime import datetime
from collections import defaultdict

# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PARENT_MIN_AGE_DIFF = 13
PARENT_MAX_AGE_DIFF = 60
TYPICAL_PARENT_AGE = 28


# --- Funciones de Carga y Guardado ---
def cargar_personas_desde_personas_json(archivo="personas.json"):
    """Carga personas desde personas.json, incluyendo todos los datos personales."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("personas.json debe contener una lista de personas")
        personas_dict = {}
        for persona in data:
            cedula = str(persona.get("cedula", "")).strip()
            if not cedula:
                continue
            # Construir nombre completo correctamente
            nombre = persona.get("nombre", "").strip()
            apellido1 = persona.get("apellido1", "").strip()
            apellido2 = persona.get("apellido2", "").strip()
            nombre_completo = f"{nombre} {apellido1} {apellido2}".strip()

            # Añadir edad
            edad = calcular_edad(persona.get("fecha_nacimiento"))

            # Guardar todos los campos
            personas_dict[cedula] = {
                "cedula": cedula,
                "nombre": nombre,
                "apellido1": apellido1,
                "apellido2": apellido2,
                "nombre_completo": nombre_completo,
                "fecha_nacimiento": persona.get("fecha_nacimiento", ""),
                "fecha_fallecimiento": persona.get("fecha_fallecimiento", None),
                "genero": persona.get("genero", "No especificado"),
                "lugar_residencia": persona.get("lugar_residencia", "No especificado"),
                "estado_civil": persona.get("estado_civil", "No especificado"),
                "edad": edad
            }
        logger.info(f"Personas cargadas desde {archivo}: {len(personas_dict)}")
        return personas_dict
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo {archivo}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar {archivo}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error inesperado al cargar personas: {e}")
        return {}


def cargar_matrimonios(archivo="matrimonios.json"):
    """Carga matrimonios desde un archivo JSON."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error("El archivo de matrimonios debe contener una lista")
                return []
            logger.info(f"Matrimonios cargados: {len(data)}")
            return data
    except FileNotFoundError:
        logger.info("Archivo de matrimonios no encontrado")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {archivo}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error al cargar matrimonios: {e}")
        return []


def guardar_relaciones(relaciones_data, archivo="relaciones.json"):
    """Guarda las relaciones inferidas en un archivo JSON."""
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(relaciones_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Relaciones guardadas en {archivo}")
    except Exception as e:
        logger.error(f"Error al guardar relaciones: {e}")


# --- Utilidades ---
def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento."""
    if not fecha_nacimiento or not isinstance(fecha_nacimiento, str):
        return None
    try:
        nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return edad if edad >= 0 else None
    except ValueError:
        return None


def apellidos_set(persona):
    """Devuelve un set con los apellidos en minúscula y sin espacios."""
    s = set()
    if not isinstance(persona, dict):
        return s
    a1 = str(persona.get('apellido1', '')).strip().lower()
    a2 = str(persona.get('apellido2', '')).strip().lower()
    if a1:
        s.add(a1)
    if a2:
        s.add(a2)
    return s


def uniq(seq):
    """Mantiene orden y quita duplicados."""
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


# --- Funciones de Inferencia de Relaciones ---
def construir_parejas(matrimonios):
    """Construye un diccionario de parejas a partir de los matrimonios registrados."""
    parejas = {}  # {cedula: cedula_pareja}
    for matrimonio in matrimonios:
        if isinstance(matrimonio, dict):
            c1 = str(matrimonio.get('conyuge1_cedula', '')).strip()
            c2 = str(matrimonio.get('conyuge2_cedula', '')).strip()
            if c1 and c2:
                parejas[c1] = c2
                parejas[c2] = c1
    logger.info(f"Parejas registradas: {len(parejas)//2} matrimonios")
    return parejas


def _score_parent_candidate(child_age, child_surnames, adult_age, adult_surnames):
    if not isinstance(adult_age, int):
        return -1
    gap = adult_age - (child_age if isinstance(child_age, int) else 0)
    if isinstance(child_age, int):
        if gap < PARENT_MIN_AGE_DIFF or gap > PARENT_MAX_AGE_DIFF:
            return -1
    overlap = len(child_surnames & adult_surnames)
    score = overlap * 10
    if isinstance(child_age, int):
        # bonificación por cercanía a edad típica
        score += max(0, 10 - abs(gap - TYPICAL_PARENT_AGE))
    return score


def inferir_padres_hijos(personas_dict, parejas):
    """
    Infiere relaciones padre-hijo con reglas más estrictas para reducir falsos positivos.
    """
    relaciones = defaultdict(lambda: {'padres': [], 'hijos': []})
    # Asegurar que todos existan en el dict
    for c in personas_dict:
        _ = relaciones[c]

    for cedula_hijo, datos_hijo in personas_dict.items():
        edad_hijo = datos_hijo.get('edad')
        apellidos_hijo = apellidos_set(datos_hijo)
        if not apellidos_hijo:
            continue

        # Candidatos individuales
        candidatos = []
        for cedula_adulto, datos_adulto in personas_dict.items():
            if cedula_adulto == cedula_hijo:
                continue
            if parejas.get(cedula_hijo) == cedula_adulto:
                continue  # jamás pareja

            edad_adulto = datos_adulto.get('edad')
            apellidos_adulto = apellidos_set(datos_adulto)
            s = _score_parent_candidate(edad_hijo, apellidos_hijo, edad_adulto, apellidos_adulto)
            if s >= 0 and len(apellidos_hijo & apellidos_adulto) >= 1:
                candidatos.append((s, cedula_adulto))

        candidatos.sort(reverse=True)

        # Intentar emparejar una pareja registrada
        mejor_par = None
        mejor_par_score = -1
        candidatos_set = {c for _, c in candidatos}
        for _, c1 in candidatos:
            c2 = parejas.get(c1)
            if not c2 or c2 not in candidatos_set or c1 == c2:
                continue
            ap1 = apellidos_set(personas_dict[c1])
            ap2 = apellidos_set(personas_dict[c2])
            union_ap = ap1 | ap2
            if not apellidos_hijo.issubset(union_ap):
                continue
            s1 = _score_parent_candidate(edad_hijo, apellidos_hijo, personas_dict[c1].get('edad'), ap1)
            s2 = _score_parent_candidate(edad_hijo, apellidos_hijo, personas_dict[c2].get('edad'), ap2)
            s_total = s1 + s2
            if s_total > mejor_par_score:
                mejor_par_score = s_total
                mejor_par = (c1, c2)

        padres_asignados = []
        if mejor_par:
            p1, p2 = mejor_par
            padres_asignados = uniq([p1, p2])
        elif candidatos:
            padres_asignados = [candidatos[0][1]]

        # Registrar relaciones
        for p in padres_asignados[:2]:
            if p not in relaciones[cedula_hijo]['padres']:
                relaciones[cedula_hijo]['padres'].append(p)
            if cedula_hijo not in relaciones[p]['hijos']:
                relaciones[p]['hijos'].append(cedula_hijo)

    logger.info("Relaciones padre-hijo inferidas.")
    return relaciones


def hermanos_de(relaciones, cedula_persona):
    """Hermanos: comparten al menos un padre con la persona."""
    hermanxs = set()
    for p in relaciones[cedula_persona]['padres']:
        for h in relaciones[p]['hijos']:
            if h != cedula_persona:
                hermanxs.add(h)
    return list(hermanxs)


def calcular_generaciones(personas_dict, relaciones):
    """Calcula la generación de cada persona usando BFS desde personas sin padres (máx 4)."""
    generaciones = defaultdict(lambda: 1)
    raices = [c for c in personas_dict if not relaciones[c]['padres']]
    for r in raices:
        generaciones[r] = 1

    from collections import deque
    q = deque([(r, 1) for r in raices])
    visitados = set(raices)
    while q:
        actual, gen = q.popleft()
        if gen >= 4:
            continue
        for hijo in relaciones[actual]['hijos']:
            if generaciones[hijo] < gen + 1:
                generaciones[hijo] = gen + 1
            if hijo not in visitados:
                visitados.add(hijo)
                q.append((hijo, gen + 1))

    for c in generaciones:
        if generaciones[c] > 4:
            generaciones[c] = 4

    return generaciones


def construir_relaciones_completas(personas_dict, matrimonios, relaciones, generaciones):
    """Construye el diccionario final de relaciones por persona."""
    parejas = construir_parejas(matrimonios)
    relaciones_finales = {}

    for cedula, datos_persona in personas_dict.items():
        # Usar nombre completo ya procesado
        nombre_completo = datos_persona["nombre_completo"]

        padres = uniq(relaciones[cedula]['padres'])
        hijos = uniq(relaciones[cedula]['hijos'])
        pareja = parejas.get(cedula)

        hermanos = uniq(hermanos_de(relaciones, cedula))

        abuelos = []
        for p in padres:
            abuelos.extend(relaciones[p]['padres'])
        abuelos = uniq([a for a in abuelos if a not in padres])

        nietos = []
        for h in hijos:
            nietos.extend(relaciones[h]['hijos'])
        nietos = uniq(nietos)

        tios = []
        for p in padres:
            tios.extend([h for h in hermanos_de(relaciones, p) if h not in padres])
        tios = uniq(tios)

        sobrinos = []
        for h in hermanos:
            sobrinos.extend(relaciones[h]['hijos'])
        sobrinos = uniq(sobrinos)

        primos = []
        for t in tios:
            primos.extend(relaciones[t]['hijos'])
        primos = uniq([p for p in primos if p != cedula and p not in hermanos])

        bisabuelos = []
        for a in abuelos:
            bisabuelos.extend(relaciones[a]['padres'])
        bisabuelos = uniq(bisabuelos)

        bisnietos = []
        for n in nietos:
            bisnietos.extend(relaciones[n]['hijos'])
        bisnietos = uniq(bisnietos)

        sobrinos_nietos = []
        for s in sobrinos:
            sobrinos_nietos.extend(relaciones[s]['hijos'])
        sobrinos_nietos = uniq(sobrinos_nietos)

        tios_abuelos = []
        for a in abuelos:
            tios_abuelos.extend(hermanos_de(relaciones, a))
        tios_abuelos = uniq(tios_abuelos)

        primos_hermanos = primos[:]
        primos_politicos = []
        for pr in primos:
            cony = parejas.get(pr)
            if cony:
                primos_politicos.append(cony)
        if pareja:
            padres_cony = relaciones[pareja]['padres']
            tios_cony = []
            for pc in padres_cony:
                tios_cony.extend([h for h in hermanos_de(relaciones, pc) if h not in padres_cony])
            primos_cony = []
            for tc in uniq(tios_cony):
                primos_cony.extend(relaciones[tc]['hijos'])
            primos_politicos.extend(primos_cony)
        primos_politicos = uniq([x for x in primos_politicos if x not in primos and x != cedula])

        relaciones_finales[cedula] = {
            "nombre": nombre_completo,
            # === Datos personales completos ===
            "fecha_nacimiento": datos_persona.get("fecha_nacimiento", ""),
            "fecha_fallecimiento": datos_persona.get("fecha_fallecimiento", None),
            "genero": datos_persona.get("genero", "No especificado"),
            "lugar_residencia": datos_persona.get("lugar_residencia", "No especificado"),
            "estado_civil": datos_persona.get("estado_civil", "No especificado"),
            # === Relaciones ===
            "relaciones": {
                "padres": padres,
                "hijos": hijos,
                "pareja": pareja,
                "hermanos": hermanos,
                "abuelos": abuelos,
                "nietos": nietos,
                "tios": tios,
                "sobrinos": sobrinos,
                "primos": primos,
                "primos_segundos": [],
                "bisabuelos": bisabuelos,
                "bisnietos": bisnietos,
                "sobrinos_nietos": sobrinos_nietos,
                "tios_abuelos": tios_abuelos,
                "primos_hermanos": primos_hermanos,
                "primos_politicos": primos_politicos,
                "generacion": generaciones.get(cedula, 3)
            }
        }

    return relaciones_finales


# --- Función Principal ---
def main():
    """Función principal para ejecutar la inferencia."""
    logger.info("--- Iniciando Inferencia Familiar ---")

    # 1. Cargar datos desde personas.json (fuente completa)
    personas_dict = cargar_personas_desde_personas_json()
    matrimonios = cargar_matrimonios("matrimonios.json")

    if not personas_dict:
        logger.error("No se pudieron cargar las personas. Finalizando.")
        return

    # 2. Construir parejas registradas
    parejas = construir_parejas(matrimonios)

    # 3. Inferir relaciones padre-hijo
    relaciones_temp = inferir_padres_hijos(personas_dict, parejas)

    # 4. Calcular generaciones
    generaciones = calcular_generaciones(personas_dict, relaciones_temp)

    # 5. Construir relaciones completas
    relaciones_completas = construir_relaciones_completas(
        personas_dict, matrimonios, relaciones_temp, generaciones
    )

    # 6. Preparar datos para guardar
    data_to_save = {
        "ultima_actualizacion": datetime.now().isoformat(),
        "relaciones_por_persona": relaciones_completas
    }

    # 7. Guardar en archivo
    guardar_relaciones(data_to_save, "relaciones.json")

    logger.info("--- Inferencia Familiar Finalizada ---")


if __name__ == "__main__":
    main()