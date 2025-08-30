# gestion_familias.py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from datos.gestor_datos import GestorDatos

class GestorFamilias:
    def __init__(self):
        self.archivo = "datos/familias.json"
        self.gestor_datos = GestorDatos()  # Integrar con la capa de datos
        self._crear_directorio_si_no_existe()
        self.familias = self._cargar_familias()
    
    def _crear_directorio_si_no_existe(self):
        """Crea el directorio datos si no existe"""
        os.makedirs("datos", exist_ok=True)
    
    def _cargar_familias(self):
        """Carga las familias desde el archivo JSON"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('familias', {})
            except:
                return {}
        return {}
    
    def _guardar_familias(self):
        """Guarda las familias en el archivo JSON"""
        data = {
            "familias": self.familias,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generar_id_familia(self):
        """Genera un ID único para la familia"""
        if not self.familias:
            return "FAM001"
        
        max_id = 0
        for id_familia in self.familias.keys():
            if id_familia.startswith('FAM'):
                try:
                    num = int(id_familia[3:])
                    max_id = max(max_id, num)
                except:
                    continue
        return f"FAM{max_id + 1:03d}"
    
    def insertar_familia(self, nombre):
        """
        Inserta una nueva familia con identificador y nombre
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la familia no puede estar vacío")
        
        # Generar ID único
        familia_id = self._generar_id_familia()
        
        # Crear familia
        nueva_familia = {
            "id": familia_id,
            "nombre": nombre.strip(),
            "miembros": [],
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Guardar
        self.familias[familia_id] = nueva_familia
        self._guardar_familias()
        
        return familia_id
    
    def obtener_familia(self, familia_id: str) -> Optional[Dict]:
        """Obtiene una familia por su ID"""
        return self.familias.get(familia_id)
    
    def listar_familias(self) -> List[Dict]:
        """Lista todas las familias"""
        return list(self.familias.values())

    #  ====== Gestion de integrantes de familias
    def insertar_miembro(self, familia_id: str, cedula: str, nombre: str, 
                        fecha_nacimiento: str, fecha_fallecimiento: str = None,
                        genero: str = "No especificado", lugar_residencia: str = "No especificado",
                        estado_civil: str = "No especificado"):
        """
        Inserta un miembro a una familia con todos los datos solicitados
        """
        if familia_id not in self.familias:
            raise ValueError("Familia no encontrada")
        
        if not cedula or not nombre or not fecha_nacimiento:
            raise ValueError("Cédula, nombre y fecha de nacimiento son obligatorios")
        
        # Validar y corregir formato de fecha de nacimiento
        fecha_nac_corregida = self._corregir_fecha(fecha_nacimiento)
        
        # Extraer apellidos del nombre (asumiendo formato: Nombre Apellido1 Apellido2)
        apellidos = self._extraer_apellidos(nombre)
        
        # Crear estructura del miembro
        miembro = {
            "cedula": cedula,
            "nombre": nombre,
            "apellido1": apellidos[0] if len(apellidos) > 0 else "",
            "apellido2": apellidos[1] if len(apellidos) > 1 else "",
            "fecha_nacimiento": fecha_nac_corregida,
            "fecha_fallecimiento": fecha_fallecimiento,
            "genero": genero,
            "lugar_residencia": lugar_residencia,
            "estado_civil": estado_civil,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Agregar a la familia
        self.familias[familia_id]["miembros"].append(miembro)
        self.familias[familia_id]["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d")
        self._guardar_familias()
        
        return miembro
    
    def editar_miembro(self, familia_id: str, cedula: str, nombre: str,
                       fecha_nacimiento: str, fecha_fallecimiento: str = None,
                       genero: str = "No especificado", lugar_residencia: str = "No especificado",
                       estado_civil: str = "No especificado"):
        """
        Edita los datos de un miembro existente en una familia.
        La cédula no se puede cambiar y se usa como identificador.
        """
        if familia_id not in self.familias:
            raise ValueError("Familia no encontrada")

        if not cedula or not nombre or not fecha_nacimiento:
            raise ValueError("Cédula, nombre y fecha de nacimiento son obligatorios")

        familia = self.familias[familia_id]
        for i, miembro in enumerate(familia["miembros"]):
            # Comparar cédulas como strings, eliminando espacios
            if str(miembro.get("cedula", "")).strip() == str(cedula).strip():
                # Extraer apellidos del nombre
                apellidos = self._extraer_apellidos(nombre)

                # Actualizar datos del miembro
                familia["miembros"][i].update({
                    "nombre": nombre,
                    "apellido1": apellidos[0] if len(apellidos) > 0 else "",
                    "apellido2": apellidos[1] if len(apellidos) > 1 else "",
                    "fecha_nacimiento": self._corregir_fecha(fecha_nacimiento),
                    "fecha_fallecimiento": fecha_fallecimiento,
                    "genero": genero,
                    "lugar_residencia": lugar_residencia,
                    "estado_civil": estado_civil,
                    "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d")
                })
                
                familia["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d")
                self._guardar_familias()
                return familia["miembros"][i]  # Devolver el miembro actualizado

        raise ValueError(f"Miembro con cédula {cedula} no encontrado en la familia {familia_id}")

    def eliminar_miembro(self, familia_id: str, cedula: str):
        """
        Elimina un miembro de una familia por su cédula.
        """
        if familia_id not in self.familias:
            raise ValueError("Familia no encontrada")

        familia = self.familias[familia_id]
        for i, miembro in enumerate(familia["miembros"]):
            # Comparar cédulas como strings, eliminando espacios
            if str(miembro.get("cedula", "")).strip() == str(cedula).strip():
                # Eliminar el miembro
                del familia["miembros"][i]
                familia["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d")
                self._guardar_familias()
                return True  # Indicar que se eliminó correctamente

        raise ValueError(f"Miembro con cédula {cedula} no encontrado en la familia {familia_id}")

    def _corregir_fecha(self, fecha_str: str) -> str:
        """Corrige el formato de fecha si es necesario"""
        if not fecha_str:
            return ""
        
        # Si es solo un año, convertir a formato completo
        if len(fecha_str) == 4 and fecha_str.isdigit():
            return f"{fecha_str}-01-01"
        
        # Si ya está en formato correcto
        if len(fecha_str) == 10 and fecha_str[4] == '-' and fecha_str[7] == '-':
            return fecha_str
            
        return fecha_str  # Devolver tal cual si no podemos corregirlo
    
    def _extraer_apellidos(self, nombre_completo: str) -> List[str]:
        """Extrae apellidos del nombre completo"""
        partes = nombre_completo.strip().split()
        if len(partes) <= 1:
            return ["", ""]
        elif len(partes) == 2:
            return [partes[1], ""]
        else:
            return [partes[1], partes[2]]
    
    def obtener_miembros(self, familia_id: str) -> List[Dict]:
        """Obtiene todos los miembros de una familia"""
        if familia_id not in self.familias:
            raise ValueError("Familia no encontrada")
        return self.familias[familia_id]["miembros"]
    
    # ===== NUEVOS MÉTODOS PARA GESTIÓN DE RELACIONES =====
    
    def registrar_padres(self, hijo_id: str, padres_ids: List[str], tipo: str = "biológico"):
        """
        Registra padres para un hijo
        
        Args:
            hijo_id: ID del hijo
            padres_ids: Lista de IDs de los padres
            tipo: "biológico" o "adoptivo"
        """
        for padre_id in padres_ids:
            self.gestor_datos.registrar_relacion(padre_id, "padre", hijo_id, tipo)
    
    def registrar_hijo(self, padre_id: str, hijo_id: str, tipo: str = "biológico"):
        """
        Registra un hijo para un padre
        
        Args:
            padre_id: ID del padre
            hijo_id: ID del hijo
            tipo: "biológico" o "adoptivo"
        """
        self.gestor_datos.registrar_relacion(padre_id, "padre", hijo_id, tipo)
    
    def registrar_hermanos(self, lista_ids: List[str]):
        """
        Registra relaciones de hermandad entre múltiples personas
        
        Args:
            lista_ids: Lista de IDs de personas hermanas
        """
        self.gestor_datos.registrar_hermanos_multiples(lista_ids)
    
    def registrar_pareja(self, persona1_id: str, persona2_id: str, tipo_union: str = "casado"):
        """
        Registra una unión de pareja entre dos personas
        
        Args:
            persona1_id: ID de la primera persona
            persona2_id: ID de la segunda persona
            tipo_union: "casado" o "unión libre"
        """
        self.gestor_datos.registrar_relacion(persona1_id, "pareja", persona2_id, tipo_union)
    
    def obtener_todas_las_personas(self) -> List[str]:
        """Obtiene todas las personas registradas"""
        return self.gestor_datos.obtener_todas_las_personas()
    
    def obtener_relaciones_de_persona(self, persona_id: str) -> Dict:
        """Obtiene las relaciones de una persona"""
        return self.gestor_datos.obtener_relaciones_de_persona(persona_id)
