# datos/gestor_datos.py
import json
import os
from tkinter import messagebox
from typing import List, Dict, Any

class GestorDatos:
    def __init__(self):
        self.relaciones_file = "relaciones.json"
        self._crear_archivo_si_no_existe()
    
    def _crear_archivo_si_no_existe(self):
        """Crea el archivo relaciones.json si no existe"""
        if not os.path.exists(self.relaciones_file):
            data = {
                "relaciones_por_persona": {},
                "registros_relaciones": []
            }
            self._guardar_datos(data)
    
    def _cargar_datos(self) -> Dict:
        """Carga todos los datos del archivo"""
        try:
            with open(self.relaciones_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # Si hay error, crear estructura básica
            data = {
                "relaciones_por_persona": {},
                "registros_relaciones": []
            }
            self._guardar_datos(data)
            return data
    
    def _guardar_datos(self, data: Dict):
        """Guarda todos los datos en el archivo"""
        try:
            with open(self.relaciones_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Error al guardar datos: {e}")
    
    def cargar_relaciones(self):
        """Carga relaciones.json (método existente)"""
        try:
            with open("relaciones.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("relaciones_por_persona", {})
        except FileNotFoundError:
            raise Exception("No se encontró 'relaciones.json'. Ejecuta primero la inferencia.")
        except json.JSONDecodeError as e:
            raise Exception(f"Error en formato JSON: {e}")
        except Exception as e:
            raise Exception(f"Error al cargar datos: {e}")
    
    def registrar_relacion(self, persona_id: str, relacion: str, con: str, tipo: str = "biológico"):
        """
        Registra una relación entre dos personas y su recíproca
        """
        # Validar que no sea la misma persona
        if persona_id == con:
            raise ValueError("No se puede registrar una relación consigo mismo")
        
        # Cargar datos existentes
        data = self._cargar_datos()
        
        # Asegurar que existan las estructuras necesarias
        if "registros_relaciones" not in data:  # ← CORREGIDO: faltaba "data"
            data["registros_relaciones"] = []
        if "relaciones_por_persona" not in data:  # ← CORREGIDO: faltaba "data"
            data["relaciones_por_persona"] = {}
        
        # Validar duplicados
        if self._existe_relacion(data, persona_id, relacion, con):
            raise ValueError(f"La relación {relacion} entre {persona_id} y {con} ya existe")
        
        # Validar bucles (para relaciones parentales)
        if relacion in ["padre", "hijo"] and self._forma_bucle(data, persona_id, con):
            raise ValueError("No se puede crear un bucle genealógico")
        
        # Registrar relación principal
        registro_principal = {
            "persona_id": persona_id,
            "relacion": relacion,
            "con": con,
            "tipo": tipo
        }
        
        # Registrar relación recíproca
        relacion_reciproca = self._obtener_relacion_reciproca(relacion)
        registro_reciproco = {
            "persona_id": con,
            "relacion": relacion_reciproca,
            "con": persona_id,
            "tipo": tipo
        }
        
        # Agregar registros
        data["registros_relaciones"].append(registro_principal)
        data["registros_relaciones"].append(registro_reciproco)
        
        # Actualizar relaciones por persona
        self._actualizar_relaciones_por_persona(data, persona_id, relacion, con, tipo)
        self._actualizar_relaciones_por_persona(data, con, relacion_reciproca, persona_id, tipo)
        
        # Guardar cambios
        self._guardar_datos(data)
        
        return True
        
    
    
    def _existe_relacion(self, data: Dict, persona_id: str, relacion: str, con: str) -> bool:
        """Verifica si ya existe una relación específica"""
        registros = data.get("registros_relaciones", [])
        for registro in registros:
            if (registro.get("persona_id") == persona_id and 
                registro.get("relacion") == relacion and 
                registro.get("con") == con):
                return True
        return False
    
    def _forma_bucle(self, data: Dict, persona_id: str, con: str) -> bool:
        """Verifica si crear esta relación formaría un bucle"""
        # Verificar si 'con' es ancestro de 'persona_id'
        ancestros = self._obtener_ancestros(data, persona_id)
        if con in ancestros:
            return True
        
        # Verificar si 'persona_id' es ancestro de 'con'
        ancestros_con = self._obtener_ancestros(data, con)
        if persona_id in ancestros_con:
            return True
            
        return False
    
    def _obtener_ancestros(self, data: Dict, persona_id: str) -> set:
        """Obtiene todos los ancestros de una persona"""
        ancestros = set()
        visitados = set()
        
        def dfs(actual):
            if actual in visitados:
                return
            visitados.add(actual)
            
            # Buscar padres
            registros = data.get("registros_relaciones", [])
            for registro in registros:
                if (registro.get("persona_id") == actual and 
                    registro.get("relacion") == "hijo"):
                    padre = registro.get("con")
                    if padre:
                        ancestros.add(padre)
                        dfs(padre)
        
        dfs(persona_id)
        return ancestros
    
    def _obtener_relacion_reciproca(self, relacion: str) -> str:
        """Obtiene la relación recíproca"""
        reciprocas = {
            "padre": "hijo",
            "hijo": "padre",
            "hermano": "hermano",
            "pareja": "pareja"
        }
        return reciprocas.get(relacion, relacion)
    
    def _actualizar_relaciones_por_persona(self, data: Dict, persona_id: str, relacion: str, con: str, tipo: str):
        """Actualiza el diccionario de relaciones por persona"""
        if "relaciones_por_persona" not in data:  # ← CORREGIDO: faltaba "data"
            data["relaciones_por_persona"] = {}
            
        if persona_id not in data["relaciones_por_persona"]:
            data["relaciones_por_persona"][persona_id] = {
                "nombre": f"Persona {persona_id}",  # Se actualizará con datos reales
                "relaciones": {
                    "padres": [],
                    "hijos": [],
                    "hermanos": [],
                    "pareja": None,
                    "abuelos": [],
                    "nietos": [],
                    "tios": [],
                    "sobrinos": [],
                    "primos": [],
                    "generacion": 0
                }
            }
        
        relaciones = data["relaciones_por_persona"][persona_id]["relaciones"]
        
        # Actualizar según el tipo de relación
        if relacion == "padre":
            if con not in relaciones["padres"]:
                relaciones["padres"].append(con)
        elif relacion == "hijo":
            if con not in relaciones["hijos"]:
                relaciones["hijos"].append(con)
        elif relacion == "hermano":
            if con not in relaciones["hermanos"]:
                relaciones["hermanos"].append(con)
        elif relacion == "pareja":
            relaciones["pareja"] = con
    
    def registrar_hermanos_multiples(self, lista_ids: List[str]):
        """Registra relaciones de hermandad entre múltiples personas"""
        if len(lista_ids) < 2:
            raise ValueError("Se necesitan al menos 2 personas para registrar hermandad")
        
        # Registrar hermandad entre todas las combinaciones
        for i in range(len(lista_ids)):
            for j in range(i + 1, len(lista_ids)):
                self.registrar_relacion(lista_ids[i], "hermano", lista_ids[j], "biológico")
    
    def obtener_todas_las_personas(self) -> List[str]:
        """Obtiene todas las personas registradas en relaciones"""
        try:
            data = self._cargar_datos()
            personas = set()
            registros = data.get("registros_relaciones", [])
            for registro in registros:
                personas.add(registro.get("persona_id", ""))
                personas.add(registro.get("con", ""))
            return [p for p in personas if p]  # Filtrar strings vacíos
        except:
            return []
    
    def obtener_relaciones_de_persona(self, persona_id: str) -> Dict:
        """Obtiene todas las relaciones de una persona"""
        try:
            data = self._cargar_datos()
            return data.get("relaciones_por_persona", {}).get(persona_id, {
                "nombre": f"Persona {persona_id}",
                "relaciones": {
                    "padres": [],
                    "hijos": [],
                    "hermanos": [],
                    "pareja": None,
                    "abuelos": [],
                    "nietos": [],
                    "tios": [],
                    "sobrinos": [],
                    "primos": [],
                    "generacion": 0
                }
            })
        except:
            return {
                "nombre": f"Persona {persona_id}",
                "relaciones": {
                    "padres": [],
                    "hijos": [],
                    "hermanos": [],
                    "pareja": None,
                    "abuelos": [],
                    "nietos": [],
                    "tios": [],
                    "sobrinos": [],
                    "primos": [],
                    "generacion": 0
                }
            }