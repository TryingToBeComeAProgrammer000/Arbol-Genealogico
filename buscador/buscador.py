# buscador.py
import json
from datetime import datetime, timedelta

class BuscadorFamiliar:
    def __init__(self, relaciones_file="relaciones.json", familias_file="datos/familias.json"):
        """
        Inicializa el buscador cargando las relaciones y datos de personas desde familias.json.
        """
        self.relaciones_file = relaciones_file
        self.familias_file = familias_file
        self.relaciones = self._cargar_relaciones()
        self.personas_dict = self._cargar_personas_desde_familias()

    def _cargar_relaciones(self):
        """Carga el archivo relaciones.json"""
        try:
            with open(self.relaciones_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data["relaciones_por_persona"]
        except Exception as e:
            raise Exception(f"Error al cargar relaciones.json: {e}")

    def _cargar_personas_desde_familias(self):
        """
        Carga personas desde familias.json y las organiza en un diccionario por cédula.
        """
        try:
            with open(self.familias_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            personas_dict = {}
            familias = data.get("familias", {})

            for familia in familias.values():
                miembros = familia.get("miembros", [])
                for persona in miembros:
                    cedula = str(persona.get("cedula"))  # Convertir a string para consistencia
                    if cedula:
                        personas_dict[cedula] = persona

            return personas_dict

        except Exception as e:
            raise Exception(f"Error al cargar familias.json: {e}")

    def _calcular_edad(self, persona, fecha_referencia=None):
        """Calcula la edad a partir de la fecha de nacimiento. Usa hoy si no hay fallecimiento."""
        if not fecha_referencia:
            fecha_referencia = datetime.now()

        fecha_nac = persona.get("fecha_nacimiento")
        if not fecha_nac:
            return None

        try:
            nac = datetime.strptime(fecha_nac, "%Y-%m-%d")
            edad = fecha_referencia.year - nac.year - ((fecha_referencia.month, fecha_referencia.day) < (nac.month, nac.day))
            return edad if edad >= 0 else None
        except ValueError:
            return None

    def _existe(self, cedula):
        """Verifica que una cédula esté en las relaciones."""
        if cedula not in self.relaciones:
            raise ValueError(f"Persona con cédula {cedula} no encontrada.")
        return True

    def _nombre(self, cedula):
        """Obtiene nombre de la persona por cédula."""
        return self.relaciones.get(cedula, {}).get("nombre", 
                self.personas_dict.get(str(cedula), {}).get("nombre", cedula))

    # ===================================================================
    # CONSULTAS PEDIDAS (con adaptaciones para la nueva estructura)
    # ===================================================================

    def relacion_entre(self, cedula_a, cedula_b):
        """1. ¿Cuál es la relación entre persona A y persona B?"""
        self._existe(cedula_a)
        self._existe(cedula_b)

        if cedula_a == cedula_b:
            return "Misma persona"

        # Relaciones directas
        rels_a = self.relaciones[cedula_a]["relaciones"]

        if cedula_b in rels_a["padres"]:
            return f"{self._nombre(cedula_b)} es padre/madre de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["hijos"]:
            return f"{self._nombre(cedula_b)} es hijo(a) de {self._nombre(cedula_a)}"
        if cedula_b == rels_a["pareja"]:
            return f"{self._nombre(cedula_b)} es pareja de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["hermanos"]:
            return f"{self._nombre(cedula_b)} es hermano(a) de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["abuelos"]:
            return f"{self._nombre(cedula_b)} es abuelo(a) de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["nietos"]:
            return f"{self._nombre(cedula_b)} es nieto(a) de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["tios"]:
            return f"{self._nombre(cedula_b)} es tío(a) de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["sobrinos"]:
            return f"{self._nombre(cedula_b)} es sobrino(a) de {self._nombre(cedula_a)}"
        if cedula_b in rels_a["primos"]:
            return f"{self._nombre(cedula_b)} es primo(a) de {self._nombre(cedula_a)}"

        # Búsqueda inversa (por si B tiene una relación con A)
        rels_b = self.relaciones[cedula_b]["relaciones"]

        if cedula_a in rels_b["padres"]:
            return f"{self._nombre(cedula_a)} es padre/madre de {self._nombre(cedula_b)}"
        if cedula_a in rels_b["hijos"]:
            return f"{self._nombre(cedula_a)} es hijo(a) de {self._nombre(cedula_b)}"
        if cedula_a in rels_b["hermanos"]:
            return f"{self._nombre(cedula_a)} es hermano(a) de {self._nombre(cedula_b)}"
        if cedula_a in rels_b["abuelos"]:
            return f"{self._nombre(cedula_a)} es abuelo(a) de {self._nombre(cedula_b)}"
        if cedula_a in rels_b["tios"]:
            return f"{self._nombre(cedula_a)} es tío(a) de {self._nombre(cedula_b)}"
        if cedula_a in rels_b["primos"]:
            return f"{self._nombre(cedula_a)} es primo(a) de {self._nombre(cedula_b)}"

        return "No se encontró relación directa"

    def primos_de(self, cedula):
        """2. ¿Quiénes son los primos de primer grado de X?"""
        self._existe(cedula)
        primos = self.relaciones[cedula]["relaciones"]["primos"]
        return [(p, self._nombre(p)) for p in primos]

    def antepasados_maternos(self, cedula):
        """3. ¿Cuáles son todos los antepasados maternos de X?"""
        self._existe(cedula)
        resultado = []

        # Obtener madre
        padres = self.relaciones[cedula]["relaciones"]["padres"]
        madre = None
        for p in padres:
            persona_p = self.personas_dict.get(str(p), {})
            # Adaptado para la nueva estructura
            genero = persona_p.get("genero", "").lower()
            apellido2 = str(persona_p.get("lugar_residencia", "")).lower()  # Usar lugar_residencia temporalmente
            
            if genero == "femenino" or genero == "mujer" or "ma" in apellido2:
                madre = p
                break
        
        # Si no hay género claro, tomar el primer padre
        if not madre and padres:
            madre = padres[0]

        if madre:
            resultado.append((madre, self._nombre(str(madre))))
            # Abuela materna
            abuelos_maternos = self.relaciones[str(madre)]["relaciones"]["padres"]
            for abuela in abuelos_maternos:
                resultado.append((abuela, self._nombre(str(abuela))))
                # Bisabuela materna
                bisabuelos = self.relaciones[str(abuela)]["relaciones"]["padres"]
                for bisabuela in bisabuelos:
                    resultado.append((bisabuela, self._nombre(str(bisabuela))))

        return list(set(resultado))  # Eliminar duplicados

    def descendientes_vivos(self, cedula):
        """4. ¿Cuáles descendientes de X están vivos actualmente?"""
        self._existe(cedula)
        vivos = []

        def dfs(persona):
            # Asegurar que persona sea string
            persona = str(persona)
            if persona not in self.relaciones:
                return
                
            hijos = self.relaciones[persona]["relaciones"]["hijos"]
            for hijo in hijos:
                hijo = str(hijo)
                # Aquí asumimos que si no tiene 'fallecido' o fecha_fallecimiento, está vivo
                datos = self.personas_dict.get(hijo, {})
                fallecido = datos.get("fecha_fallecimiento") or datos.get("fallecido")
                if not fallecido:
                    vivos.append((hijo, self._nombre(hijo)))
                    dfs(hijo)  # recursión

        dfs(cedula)
        return vivos

    def nacidos_ultimos_10_anios(self):
        """5. ¿Cuántas personas nacieron en los últimos 10 años?"""
        hace_10 = datetime.now() - timedelta(days=365 * 10)
        recientes = []
        for cedula, datos in self.personas_dict.items():
            fecha_nac = datos.get("fecha_nacimiento")
            if not fecha_nac:
                continue
            try:
                nac = datetime.strptime(fecha_nac, "%Y-%m-%d")
                if nac >= hace_10:
                    recientes.append((cedula, self._nombre(str(cedula)), fecha_nac))
            except ValueError:
                continue
        return recientes

    def parejas_con_2_o_mas_hijos(self):
        """6. ¿Cuáles parejas actuales tienen 2 o más hijos en común?"""
        resultado = []
        for cedula, datos in self.relaciones.items():
            pareja = datos["relaciones"]["pareja"]
            if not pareja:
                continue
            if cedula > pareja:  # Evitar duplicados (A-B y B-A)
                continue

            hijos_propios = set(datos["relaciones"]["hijos"])
            hijos_pareja = set(self.relaciones[pareja]["relaciones"]["hijos"])
            hijos_comunes = hijos_propios & hijos_pareja

            if len(hijos_comunes) >= 2:
                nombres_hijos = [self._nombre(str(h)) for h in hijos_comunes]
                resultado.append({
                    "pareja": f"{self._nombre(cedula)} y {self._nombre(pareja)}",
                    "hijos_comunes": len(hijos_comunes),
                    "nombres_hijos": nombres_hijos
                })
        return resultado

    def fallecidos_menos_50(self):
        """7. ¿Cuántas personas fallecieron antes de cumplir 50 años?"""
        conteo = 0
        detalles = []
        for cedula, datos in self.personas_dict.items():
            # Verificar si está fallecido
            fallecido = datos.get("fecha_fallecimiento") or datos.get("fallecido")
            if not fallecido:
                continue
                
            fecha_nac = datos.get("fecha_nacimiento")
            fecha_fall = datos.get("fecha_fallecimiento") or fallecido
            if not fecha_nac or not fecha_fall:
                continue
            try:
                nac = datetime.strptime(fecha_nac, "%Y-%m-%d")
                fall = datetime.strptime(fecha_fall, "%Y-%m-%d")
                edad = fall.year - nac.year - ((fall.month, fall.day) < (nac.month, nac.day))
                if edad < 50:
                    conteo += 1
                    detalles.append({
                        "cedula": cedula,
                        "nombre": self._nombre(str(cedula)),
                        "edad": edad,
                        "fallecimiento": fecha_fall
                    })
            except ValueError:
                continue
        return conteo, detalles