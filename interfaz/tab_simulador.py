# interfaz/tab_simulador.py
import tkinter as tk
from tkinter import ttk, Canvas, Scrollbar, Frame, Text, END
from PIL import Image, ImageDraw, ImageFont, ImageTk
from datetime import datetime
import random
import logging
from collections import deque
import json
import os

logger = logging.getLogger(__name__)


class TabSimulador:
    def __init__(self, parent, interfaz_principal):
        self.interfaz_principal = interfaz_principal
        self.frame = ttk.Frame(parent)
        self.canvas = None
        self.scrollbar_vertical = None
        self.scrollbar_horizontal = None
        self.img_tk = None
        self.simulacion_activa = False
        self.año_actual = 0
        self.personas = {}
        self.cedula_counter = 30000000
        self.posiciones = {}
        self._dibujo_listo = True
        self.perfil_seleccionado = None
        self._matrimonio_imgs = []
        self.cola_eventos = deque()
        self._timer_id = None

        # Afinidades posibles para todos
        self.afinidades_posibles = [
            ["música", "lectura"],
            ["deportes", "tecnología"],
            ["arte", "naturaleza"],
            ["viajes", "gastronomía"],
            ["cine", "series"]
        ]

        self._crear_widgets()

    def _crear_widgets(self):
        # Usar PanedWindow para dividir árbol y barra lateral
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Lado izquierdo: Árbol familiar ---
        frame_izq = ttk.Frame(paned)
        paned.add(frame_izq, weight=3)

        btn_frame = ttk.Frame(frame_izq)
        btn_frame.pack(fill="x", pady=5)

        self.btn_iniciar = ttk.Button(
            btn_frame,
            text="Iniciar Simulación",
            command=self.iniciar_simulacion
        )
        self.btn_iniciar.pack(side="left", padx=5)

        self.btn_detener = ttk.Button(
            btn_frame,
            text="Detener Simulación",
            command=self.detener_simulacion,
            state="disabled"
        )
        self.btn_detener.pack(side="left", padx=5)

        # ✅ Botón para reiniciar la simulación
        self.btn_reiniciar = ttk.Button(
            btn_frame,
            text="Reiniciar Simulación",
            command=self.reiniciar_simulacion,
            state="disabled"
        )
        self.btn_reiniciar.pack(side="left", padx=5)

        self.lbl_tiempo = ttk.Label(
            btn_frame,
            text="Año: 0",
            font=("Helvetica", 10, "bold")
        )
        self.lbl_tiempo.pack(side="left", padx=20)

        # Botón para cargar datos de familias
        self.btn_cargar_familias = ttk.Button(
            btn_frame,
            text="Cargar Datos de Familias",
            command=self.cargar_datos_de_familias
        )
        self.btn_cargar_familias.pack(side="left", padx=5)

        # Canvas con scroll vertical y horizontal
        contenedor = ttk.Frame(frame_izq)
        contenedor.pack(fill="both", expand=True)

        self.canvas = Canvas(contenedor, bg="white")
        self.scrollbar_vertical = Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        self.scrollbar_horizontal = Scrollbar(contenedor, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.scrollbar_vertical.set, xscrollcommand=self.scrollbar_horizontal.set)

        # Empaquetar correctamente
        self.scrollbar_vertical.pack(side="right", fill="y")
        self.scrollbar_horizontal.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # --- Lado derecho: Barra lateral (perfiles) ---
        frame_der = ttk.Frame(paned)
        paned.add(frame_der, weight=1)

        ttk.Label(frame_der, text="Personas", font=("Helvetica", 12, "bold")).pack(pady=5)

        # Lista de personas
        cols = ("Nombre", "Edad", "Género", "Estado")
        self.tree = ttk.Treeview(frame_der, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_seleccionar_persona)

        # Historial de eventos
        ttk.Label(frame_der, text="Historial de Eventos", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        self.txt_historial = Text(frame_der, height=12, wrap="word", font=("Helvetica", 9))
        self.txt_historial.pack(fill="both", expand=True, padx=10, pady=5)

        # Configurar estilos
        self.txt_historial.tag_configure("title", font=("Helvetica", 12, "bold"), foreground="blue")
        self.txt_historial.tag_configure("header", font=("Helvetica", 11, "underline"), foreground="darkgreen")

    def cargar_datos_de_familias(self):
        """Carga los datos directamente desde familias.json"""
        try:
            if not os.path.exists("datos/familias.json"):
                print("Archivo familias.json no encontrado")
                return False
                
            with open("datos/familias.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            familias = data.get("familias", {})
            self.personas = {}
            
            # Cargar todas las personas de todas las familias
            for familia_id, familia in familias.items():
                for miembro in familia.get("miembros", []):
                    cedula = str(miembro.get("cedula", ""))
                    if not cedula:
                        continue
                        
                    # Calcular edad
                    fecha_nac = miembro.get("fecha_nacimiento", "")
                    try:
                        año_nac = int(fecha_nac.split("-")[0]) if fecha_nac else datetime.now().year - 30
                        edad = datetime.now().year - año_nac
                        edad = max(1, min(120, edad))
                    except:
                        edad = random.randint(1, 100)
                    
                    # Afinidades aleatorias
                    afinidades = random.choice(self.afinidades_posibles)
                    
                    # --- Inicialización del umbral ---
                    # Umbral base es 0.90
                    umbral_base = 0.90
                    # Si ya tiene más de 40 y está soltero, aplicar penalización por edad
                    estado_civil = miembro.get("estado_civil", "Desconocido")
                    umbral_pareja = umbral_base
                    if edad >= 40 and estado_civil not in ["Casado", "Casada", "Unión Libre"]:
                         # Calcular reducciones por edad: 10% a los 40, +10% cada 3 años
                         años_exceso = edad - 40
                         reducciones = 1 + (años_exceso // 3) # 1 por los 40, más uno cada 3 años
                         for _ in range(reducciones):
                             umbral_pareja *= 0.90 # Reducción del 10%
                    
                    self.personas[cedula] = {
                        "cedula": cedula,
                        "nombre": miembro.get("nombre", f"Persona {cedula}"),
                        "edad": edad,
                        "genero": "F" if miembro.get("genero", "No especificado") == "Femenino" else "M",
                        "fallecido": bool(miembro.get("fecha_fallecimiento")),
                        "padres": [],  # Se llenará después
                        "hijos": [],   # Se llenará después
                        "pareja": None,  # Se llenará después
                        "hermanos": [],  # Se llenará después
                        "generacion": 3,  # Valor por defecto, se puede calcular
                        "afinidades": afinidades,
                        "salud_emocional": 100,
                        "lugar_residencia": miembro.get("lugar_residencia", "Desconocido"),
                        "estado_civil": estado_civil,
                        "historial": [{"año": 0, "evento": "Nacimiento", "detalle": f"Nació en {fecha_nac}"}],
                        # --- Atributo de umbral ---
                        "umbral_pareja": max(0.0, umbral_pareja), # Asegurar que no sea negativo
                        # --- Atributo para identificar la familia de origen ---
                        "familia_id": familia_id # <-- Nuevo atributo
                    }
            
            # Cargar relaciones desde relaciones.json si existe
            self._cargar_relaciones_existentes()
            
            print(f"Datos cargados: {len(self.personas)} personas")
            return True
            
        except Exception as e:
            print(f"Error al cargar datos de familias: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _cargar_relaciones_existentes(self):
        """Carga las relaciones existentes desde relaciones.json"""
        try:
            if not os.path.exists("relaciones.json"):
                return
                
            with open("relaciones.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            relaciones_por_persona = data.get("relaciones_por_persona", {})
            
            for cedula, info_relaciones in relaciones_por_persona.items():
                if cedula in self.personas:
                    relaciones = info_relaciones.get("relaciones", {})
                    self.personas[cedula]["padres"] = [str(p) for p in relaciones.get("padres", [])]
                    self.personas[cedula]["hijos"] = [str(h) for h in relaciones.get("hijos", [])]
                    self.personas[cedula]["hermanos"] = [str(h) for h in relaciones.get("hermanos", [])]
                    pareja = relaciones.get("pareja")
                    self.personas[cedula]["pareja"] = str(pareja) if pareja else None
                    
                    # --- Asegurar que el umbral exista ---
                    # Si se cargó de relaciones.json, es posible que no tenga 'umbral_pareja'
                    if "umbral_pareja" not in self.personas[cedula]:
                         self.personas[cedula]["umbral_pareja"] = 0.90
                    
                    # --- Aplicar penalización por viudez si es relevante ---
                    # Esta lógica es compleja de aplicar aquí sin el historial completo.
                    # Es más robusto manejarla en _fallecimientos cuando ocurre el evento.
                    # Por ahora, asumimos que el umbral ya está correctamente calculado
                    # o se corregirá dinámicamente al ocurrir el fallecimiento.

                    # Actualizar relaciones recíprocas
                    for padre_ced in self.personas[cedula]["padres"]:
                        if padre_ced in self.personas and cedula not in self.personas[padre_ced]["hijos"]:
                            self.personas[padre_ced]["hijos"].append(cedula)
                    
                    for hijo_ced in self.personas[cedula]["hijos"]:
                        if hijo_ced in self.personas and cedula not in self.personas[hijo_ced]["padres"]:
                            self.personas[hijo_ced]["padres"].append(cedula)
                    
                    for hermano_ced in self.personas[cedula]["hermanos"]:
                        if hermano_ced in self.personas and cedula not in self.personas[hermano_ced]["hermanos"]:
                            self.personas[hermano_ced]["hermanos"].append(cedula)
                    
                    if self.personas[cedula]["pareja"]:
                        pareja_ced = self.personas[cedula]["pareja"]
                        if pareja_ced in self.personas:
                            self.personas[pareja_ced]["pareja"] = cedula
                            # Asegurar que ambos tengan el umbral inicializado si falta
                            if "umbral_pareja" not in self.personas[pareja_ced]:
                                self.personas[pareja_ced]["umbral_pareja"] = 0.90
            
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar relaciones existentes: {e}")

    def _on_seleccionar_persona(self, event):
        """Se llama cuando se selecciona una persona en la lista"""
        selected = self.tree.selection()
        if not selected:
            return
        try:
            item = self.tree.item(selected[0])
            cedula = str(item["tags"][0])
            self.perfil_seleccionado = cedula
            self._actualizar_vista_historial()
        except Exception as e:
            print(f"Error al seleccionar persona: {e}")

    def _actualizar_vista_historial(self):
        """Muestra perfil completo + historial de la persona seleccionada"""
        self.txt_historial.delete(1.0, "end")

        if not self.perfil_seleccionado or str(self.perfil_seleccionado) not in self.personas:
            self.txt_historial.insert("end", "Seleccione una persona de la lista para ver su historial.\n")
            return

        p = self.personas[str(self.perfil_seleccionado)]
        nombre = p["nombre"]
        edad = p["edad"]
        genero = "Femenino" if p["genero"] == "F" else "Masculino"
        estado = "Fallecido" if p["fallecido"] else "Vivo"
        pareja = self.personas.get(p["pareja"])["nombre"] if p["pareja"] and p["pareja"] in self.personas else "Ninguna"
        lugar = p.get("lugar_residencia", "Desconocido")
        generacion = p.get("generacion", "?")
        afinidades = ", ".join(p.get("afinidades", []))

        # Datos personales
        self.txt_historial.insert("end", f"PERFIL DE {nombre.upper()}\n", "title")
        self.txt_historial.insert("end", f"Edad: {edad} años\n")
        self.txt_historial.insert("end", f"Género: {genero}\n")
        self.txt_historial.insert("end", f"Estado: {estado}\n")
        self.txt_historial.insert("end", f"Lugar de residencia: {lugar}\n")
        self.txt_historial.insert("end", f"Generación: {generacion}\n")
        self.txt_historial.insert("end", f"Pareja: {pareja}\n")
        self.txt_historial.insert("end", f"Afinidades: {afinidades}\n\n")

        # Historial de eventos (ordenado por año)
        historial = sorted(p.get("historial", []), key=lambda x: x.get("año", 0))
        if historial:
            self.txt_historial.insert("end", "HISTORIAL DE EVENTOS\n", "header")
            for evento in historial:
                año = evento.get("año", "?")
                ev = evento.get("evento", "Desconocido")
                det = evento.get("detalle", "Sin detalle")
                self.txt_historial.insert("end", f"• Año {año}: {ev}\n")
                self.txt_historial.insert("end", f"  → {det}\n\n")
        else:
            self.txt_historial.insert("end", "Esta persona no tiene eventos registrados.\n")

    def actualizar_lista_personas(self):
        """Actualiza la lista de personas en la barra lateral"""
        self.tree.delete(*self.tree.get_children())
        for cedula, p in self.personas.items():
           
            estado = "Fallecido" if p["fallecido"] else ("Casado/a" if p["pareja"] else "Soltero/a")
            valores = (
                p["nombre"],
                p["edad"],
                "Femenino" if p["genero"] == "F" else "Masculino",
                "Casado/a" if p["pareja"] else "Soltero/a",
                estado
            )
            self.tree.insert("", "end", values=valores, tags=(str(cedula),))

    def iniciar_simulacion(self):
        if self.simulacion_activa:
            return

        # Cargar datos de familias al iniciar
        if not self.cargar_datos_de_familias():
            print("No se pudieron cargar los datos de familias")
            return

        self.simulacion_activa = True
    
        self.btn_iniciar.config(state="disabled")
        self.btn_detener.config(state="normal")
        self.btn_reiniciar.config(state="normal")  # Habilitar botón de reiniciar
        self.btn_cargar_familias.config(state="disabled")

        self._dibujar_arbol()
        self.actualizar_lista_personas()

        # Seleccionar automáticamente la primera persona
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            item = self.tree.item(children[0])
            self.perfil_seleccionado = str(item["tags"][0])
            self._actualizar_vista_historial()

        self._avanzar_tiempo()

    def detener_simulacion(self):
        self.simulacion_activa = False
        self.btn_iniciar.config(state="normal")
        self.btn_detener.config(state="disabled")
        self.btn_cargar_familias.config(state="normal")
        # Mantener el botón de reiniciar habilitado para poder reiniciar

        if self._timer_id is not None:
            self.frame.after_cancel(self._timer_id)
            self._timer_id = None

        # Limpiar hijos temporales
        cedulas_originales = set(str(key) for key in self.personas.keys())
        cedulas_temporales = [c for c in self.personas.keys() if c not in cedulas_originales]
        for cedula in cedulas_temporales:
            if cedula in self.personas:
                hijo = self.personas[cedula]
                for padre_ced in hijo["padres"]:
                    if padre_ced in self.personas and cedula in self.personas[padre_ced]["hijos"]:
                        self.personas[padre_ced]["hijos"].remove(cedula)
                del self.personas[cedula]
        logger.info(f"{len(cedulas_temporales)} hijos temporales eliminados")

    def reiniciar_simulacion(self):
        """Reinicia la simulación desde cero"""
        # Detener la simulación si está activa
        if self.simulacion_activa:
            self.detener_simulacion()
        
        if self._timer_id is not None:
            self.frame.after_cancel(self._timer_id)
            self._timer_id = None

        # Reiniciar variables
        self.año_actual = 0
        self.lbl_tiempo.config(text="Año: 0")
        self.personas = {}
        self.posiciones = {}
        self.perfil_seleccionado = None
        self.cedula_counter = 30000000
        
        # Limpiar canvas
        if self.canvas:
            self.canvas.delete("all")
        
        # Limpiar lista de personas
        if self.tree:
            self.tree.delete(*self.tree.get_children())
        
        # Limpiar historial
        if self.txt_historial:
            self.txt_historial.delete(1.0, "end")
        
        # Limpiar imágenes de matrimonio
        self._matrimonio_imgs = []
        
        print("Simulación reiniciada")

    def _avanzar_tiempo(self):
        # NO HAY un 'if not self.simulacion_activa: return' prematuro aquí
        self.año_actual += 1
        self.lbl_tiempo.config(text=f"Año: {self.año_actual}")

        self._cumpleaños()
        self._fallecimientos()
        self._uniones_pareja()
        self._nacimientos()
        self._dibujar_arbol()
        self.actualizar_lista_personas()

        if self.perfil_seleccionado:
            self._actualizar_vista_historial()

        self._timer_id = self.frame.after(10000, self._avanzar_tiempo)
                
    def _cumpleaños(self):
        for p in list(self.personas.values()):
            if not p["fallecido"]:
                edad_anterior = p["edad"]
                p["edad"] += 1
                if p["pareja"] is None and p["edad"] > 30:
                    p["salud_emocional"] = max(50, p["salud_emocional"] - 2)
                self._registrar_evento(p["cedula"], "Cumpleaños", f"Cumplió {p['edad']} años")

                # --- Actualizar umbral por edad ---
                # Verificar si la persona cumplió 40 o múltiplos de 3 años después de los 40
                if p["pareja"] is None and p["edad"] >= 40:
                    # Calcular el umbral base (0.90) y aplicar todas las penalizaciones hasta la edad actual
                    umbral_calculado = 0.90
                    if p["edad"] >= 40:
                        # Penalización a los 40 años
                        umbral_calculado *= 0.90
                        # Penalizaciones adicionales cada 3 años después de los 40
                        años_exceso = p["edad"] - 40
                        reducciones_adicionales = años_exceso // 3
                        for _ in range(reducciones_adicionales):
                            umbral_calculado *= 0.90
                    
                    # Actualizar el umbral en el objeto de la persona
                    p["umbral_pareja"] = max(0.0, umbral_calculado)
                    # print(f"Umbral actualizado para {p['nombre']} (edad {p['edad']}, soltero): {p['umbral_pareja']:.4f}") # Para depuración

    def _fallecimientos(self):
        for cedula in list(self.personas.keys()):
            if cedula not in self.personas:  # Protección contra eliminación concurrente
                continue
            p = self.personas[cedula]
            if p["fallecido"]:
                continue
            prob = 0.02 if p["edad"] > 75 else 0.005 if p["edad"] > 60 else 0.001
            if random.random() < prob:
                p["fallecido"] = True
                self._registrar_evento(cedula, "Fallecimiento", "Falleció")

                if p["pareja"]:
                    pareja_ced = p["pareja"]
                    pareja = self.personas.get(pareja_ced)
                    if pareja:
                        pareja["estado_civil"] = "Viudo"
                        self._registrar_evento(pareja_ced, "Viudez", f"Falleció {p['nombre']}")
                        
                        # --- Actualizar umbral del sobreviviente por viudez ---
                        # Reducir el umbral en un 40% del valor actual
                        if "umbral_pareja" in pareja:
                            pareja["umbral_pareja"] *= 0.60 # Equivalente a reducir un 40%
                            pareja["umbral_pareja"] = max(0.0, pareja["umbral_pareja"])
                            # print(f"Umbral reducido por viudez para {pareja['nombre']}: {pareja['umbral_pareja']:.4f}") # Para depuración
                        else:
                            # Si no existía, inicializarlo y aplicar la penalización
                            pareja["umbral_pareja"] = 0.90 * 0.60 # 0.54
                        

                # Si es padre y ambos padres mueren → asignar tutor
                self._asignar_tutor_si_necesario(p)

    def _asignar_tutor_si_necesario(self, fallecido):
        """Asigna tutor a hijos si ambos padres mueren"""
        if fallecido["genero"] not in ["M", "F"]:  # Solo adultos
            return

        # Buscar hijos que quedan huérfanos
        for hijo_ced in fallecido["hijos"]:
            if hijo_ced not in self.personas:
                continue
            hijo = self.personas[hijo_ced]

            # Verificar si ambos padres murieron
            padres_vivos = [p for p in hijo["padres"] if p in self.personas and not self.personas[p]["fallecido"]]
            if len(padres_vivos) == 0 and len(hijo["padres"]) >= 2:
                # Buscar tutor: hermano mayor o tío
                tutor = self._buscar_tutor(hijo)
                if tutor:
                    # Registrar en historial
                    self._registrar_evento(hijo_ced, "Tutela asignada", f"Quedó bajo tutela de {tutor['nombre']}")
                    self._registrar_evento(tutor["cedula"], "Tutoría", f"Se convirtió en tutor de {hijo['nombre']}")

    def _buscar_tutor(self, hijo):
        """Busca tutor entre hermanos o tíos"""
        # Prioridad 1: Hermanos mayores
        hermanos_mayores = [
            self.personas[h] for h in hijo["hermanos"]
            if h in self.personas
               and not self.personas[h]["fallecido"]
               and self.personas[h]["edad"] >= 18
        ]

        # Ordenar por edad descendente (mayor primero)
        hermanos_mayores.sort(key=lambda x: x["edad"], reverse=True)

        if hermanos_mayores:
            return hermanos_mayores[0]  # El mayor

        # Prioridad 2: Tíos
        tios_disponibles = []
        for padre_ced in hijo["padres"]:
            if padre_ced in self.personas:
                padre = self.personas[padre_ced]
                for hermano_padre_ced in padre["hermanos"]:
                    if (hermano_padre_ced in self.personas and
                            not self.personas[hermano_padre_ced]["fallecido"] and
                            self.personas[hermano_padre_ced]["edad"] >= 18):
                        tios_disponibles.append(self.personas[hermano_padre_ced])

        if tios_disponibles:
            return tios_disponibles[0]

        return None

    def _indice_compatibilidad(self, p1, p2):
        """
        Calcula compatibilidad basada en:
        - Afinidades comunes
        - Diferencia de edad
        - No parentesco directo
        """
        # Afinidades comunes
        afinidad_comun = len(set(p1["afinidades"]) & set(p2["afinidades"]))
        compatibilidad = 0.5 + afinidad_comun * 0.2  # Base + afinidades

        # Penalización por edad
        edad_diff = abs(p1["edad"] - p2["edad"])
        if edad_diff > 15:
            compatibilidad -= 0.3

        # Bloquear parentesco directo
        if p2["cedula"] in p1.get("padres", []) or p1["cedula"] in p2.get("padres", []):
            return 0  # Padre/hijo
        if p2["cedula"] in p1.get("hermanos", []) or p1["cedula"] in p2.get("hermanos", []):
            return 0  # Hermanos

        return max(0, min(1, compatibilidad))

    def _uniones_pareja(self):
        """
        Busca parejas compatibles para matrimonio (monogamia)
        Usa listas optimizadas con comprensión
        Dibuja línea de matrimonio inmediatamente
        """
        # Lista optimizada con comprensión de solteros elegibles
        solteros = [
            p for p in self.personas.values()
            if p["pareja"] is None
               and not p["fallecido"]
               and p["edad"] >= 18
        ]
        random.shuffle(solteros)

        # Lista para tracking de matrimonios recientes
        nuevos_matrimonios = []

        for i, p1 in enumerate(solteros):
            # Solo procesar si aún no tiene pareja
            if p1["pareja"] is not None:
                continue

            for p2 in solteros[i + 1:]:
                # Solo procesar si aún no tiene pareja
                if p2["pareja"] is not None:
                    continue

                # --- Verificaciones de restricciones ---
                # 1. No emparejar personas del mismo género (ya existente, reforzada)
                if p1["genero"] == p2["genero"]:
                    continue

                # 2. No emparejar personas de la misma familia
                if p1.get("familia_id") == p2.get("familia_id"):
                    continue

                # 3. No emparejar si la diferencia de edad es mayor a 15 años
                if abs(p1["edad"] - p2["edad"]) > 15:
                    continue

                # Si pasan todas las restricciones, calcular compatibilidad
                compatibilidad = self._indice_compatibilidad(p1, p2)
                
                # --- Usar umbral dinámico ---
                # Obtener los umbrales de ambas personas
                umbral_p1 = p1.get("umbral_pareja", 0.90)
                umbral_p2 = p2.get("umbral_pareja", 0.90)
                
                # Para emparejar, la compatibilidad debe superar el umbral promedio
                umbral_promedio = (umbral_p1 + umbral_p2) / 2.0
                
                if compatibilidad > umbral_promedio:
                    p1["pareja"] = p2["cedula"]
                    p2["pareja"] = p1["cedula"]
                    p1["estado_civil"] = "Casado"
                    p2["estado_civil"] = "Casado"

                    self._registrar_evento(p1["cedula"], "Matrimonio", f"Se casó con {p2['nombre']}")
                    self._registrar_evento(p2["cedula"], "Matrimonio", f"Se casó con {p1['nombre']}")

                    # Agregar a lista de nuevos matrimonios
                    nuevos_matrimonios.append((p1["cedula"], p2["cedula"]))
                    break  # Salir después de casar

        # Procesar nuevos matrimonios
        for c1, c2 in nuevos_matrimonios:
            if c1 in self.posiciones and c2 in self.posiciones:
                self._dibujar_linea_matrimonio_inmediata(c1, c2)

        # Si ocurrieron matrimonios, actualizar la lista y el árbol
        if nuevos_matrimonios:
            self.actualizar_lista_personas()
            self._dibujar_arbol()

    def _dibujar_linea_matrimonio_inmediata(self, cedula1, cedula2):
        """Dibuja la línea de matrimonio inmediatamente entre dos personas"""
        if cedula1 not in self.posiciones or cedula2 not in self.posiciones:
            return

        # Obtener coordenadas
        x1, y1 = self.posiciones[cedula1]
        x2, y2 = self.posiciones[cedula2]
        radio = 30

        # Solo dibujar si están relativamente cerca verticalmente
        if abs(y1 - y2) < 100:
            # Crear imagen temporal para dibujar la línea
            ancho_img = 1400
            alto_img = 100 + len(set(p["generacion"] for p in self.personas.values())) * 220
            imagen = Image.new("RGBA", (ancho_img, alto_img), (0, 0, 0, 0))
            draw = ImageDraw.Draw(imagen)

            # Dibujar arco de matrimonio
            self._dibujar_arco_matrimonio(draw, (x1 + radio, y1), (x2 - radio, y2), "purple", 3)

            # Convertir a PhotoImage y dibujar en canvas
            img_tk = ImageTk.PhotoImage(imagen)
            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
            # Mantener referencia para evitar garbage collection
            self._matrimonio_imgs.append(img_tk)

    def _nacimientos(self):
        """
        Permite que cualquier pareja casada con madre en edad fértil tenga hijos.
        Usa listas filtradas optimizadas
        Máximo 2 hijos por pareja
        """
        # Lista de madres elegibles optimizada
        madres_elegibles = [
            p for p in self.personas.values()
            if not p["fallecido"]
               and p["genero"] == "F"
               and p["pareja"] is not None
               and 18 <= p["edad"] <= 45
        ]

        # Procesar cada madre
        for madre in madres_elegibles:
            padre = self.personas.get(madre["pareja"])
            if not padre or padre["fallecido"]:
                continue

            # Contar hijos existentes de esta pareja
            hijos_existentes = len([h for h in madre["hijos"] if h in self.personas])
            if hijos_existentes >= 2:  # Límite de 2 hijos
                continue

            # Mayor probabilidad en 20-35 años
            prob = 0.3 if madre["edad"] < 36 else 0.1

            if random.random() < prob:
                self._crear_hijo(madre, padre)

    def _crear_hijo(self, madre, padre):
        self.cedula_counter += 1
        cedula = str(self.cedula_counter)

        # Lista ampliada de nombres
        nombres = [
            "Luis", "Ana", "Carlos", "María", "Pedro", "Sofía", "Miguel", "Laura",
            "Javier", "Valeria", "Diego", "Camila", "Andrés", "Isabella", "José",
            "Lucía", "Manuel", "Elena", "Fernando", "Adriana", "Ricardo", "Daniela",
            "Mario", "Gabriela", "Hugo", "Natalia", "Santiago", "Jimena", "Sebastián",
            "Renata", "Emilio", "Florencia", "Roberto", "Catalina", "Martín", "Abril",
            "Alejandro", "Victoria", "Tomás", "Juliana", "Daniel", "Paula", "Mauricio",
            "Clara", "Esteban", "Romina", "Gonzalo", "Agustina", "Ignacio", "Mía"
        ]
        nombre = random.choice(nombres)

        genero = "M" if nombre in ["Luis", "Carlos", "Pedro", "Miguel", "Javier", "Diego",
                                   "Andrés", "José", "Manuel", "Fernando", "Ricardo", "Mario",
                                   "Hugo", "Santiago", "Sebastián", "Emilio", "Roberto",
                                   "Martín", "Alejandro", "Tomás", "Daniel", "Mauricio",
                                   "Esteban", "Gonzalo", "Ignacio"] else "F"

        # Heredar apellidos correctamente
        apellido1 = madre.get("apellido1") or madre["nombre"].split()[-1]
        apellido2 = padre.get("apellido2") or padre["nombre"].split()[-1]

        generacion = max(madre["generacion"], padre["generacion"]) + 1

        # NO heredar afinidades → aleatorias
        afinidades = random.choice(self.afinidades_posibles)

        hijo = {
            "cedula": cedula,
            "nombre": f"{nombre} {apellido1} {apellido2}",
            "edad": 0,
            "genero": genero,
            "fallecido": False,
            "padres": [str(madre["cedula"]), str(padre["cedula"])],
            "hijos": [],
            "pareja": None,
            "hermanos": [],  # Se calculará después
            "generacion": generacion,
            "afinidades": afinidades,
            "salud_emocional": 100,
            "lugar_residencia": madre["lugar_residencia"],
            "estado_civil": "Soltero",
            "historial": [{
                "año": self.año_actual,
                "evento": "Nacimiento",
                "detalle": f"Nació de {madre['nombre']} y {padre['nombre']} (afinidades: {', '.join(afinidades)})"
            }],
            # --- Inicializar umbral para el nuevo hijo ---
            "umbral_pareja": 0.90 # Los recién nacidos (edad 0) comienzan con el umbral base
        }

        self.personas[cedula] = hijo
        madre["hijos"].append(cedula)
        padre["hijos"].append(cedula)

        # Calcular hermanos automáticamente
        self._actualizar_hermanos(hijo, madre, padre)

        # Registrar nacimiento en historial de padres (con más detalles)
        afinidades_txt = ", ".join(afinidades)
        detalle_madre = f"Tuvo un hijo: {nombre} {apellido1} {apellido2} (afinidades: {afinidades_txt})"
        detalle_padre = f"Tuvo un hijo: {nombre} {apellido1} {apellido2} (afinidades: {afinidades_txt})"

        self._registrar_evento(madre["cedula"], "Nacimiento hijo", detalle_madre)
        self._registrar_evento(padre["cedula"], "Nacimiento hijo", detalle_padre)

        self.actualizar_lista_personas()
        self._dibujar_arbol()

        # Si alguno de los padres está seleccionado, actualizar su historial
        if self.perfil_seleccionado in [madre["cedula"], padre["cedula"]]:
            self._actualizar_vista_historial()

    def _actualizar_hermanos(self, hijo, madre, padre):
        """Actualiza la lista de hermanos para el nuevo hijo y sus hermanos"""
        # Hermanos = otros hijos de los mismos padres
        hermanos_ceds = []
        for padre_ref in [madre, padre]:
            for otro_hijo_ced in padre_ref["hijos"]:
                if otro_hijo_ced != hijo["cedula"] and otro_hijo_ced not in hermanos_ceds:
                    hermanos_ceds.append(otro_hijo_ced)

        # Actualizar hermanos del nuevo hijo
        hijo["hermanos"] = hermanos_ceds

        # Actualizar hermanos de los demás hijos
        for hermano_ced in hermanos_ceds:
            if hermano_ced in self.personas:
                if hijo["cedula"] not in self.personas[hermano_ced]["hermanos"]:
                    self.personas[hermano_ced]["hermanos"].append(hijo["cedula"])

    def _registrar_evento(self, cedula, evento, detalle):
        cedula = str(cedula)
        if cedula in self.personas:
            if "historial" not in self.personas[cedula]:
                self.personas[cedula]["historial"] = []
            self.personas[cedula]["historial"].append({
                "año": self.año_actual,
                "evento": evento,
                "detalle": detalle
            })
            if cedula == self.perfil_seleccionado:
                self._actualizar_vista_historial()

    def _dibujar_arbol(self):
        if not self.personas:
            return

        generaciones = {}
        for p in self.personas.values():
            gen = p["generacion"]
            if gen not in generaciones:
                generaciones[gen] = []
            generaciones[gen].append(p)

        if not generaciones:
            return

        # Aumentar el ancho para árboles grandes
        ancho_img = max(1400, len(max(generaciones.values(), key=len)) * 300)
        alto_img = 100 + len(generaciones) * 220
        imagen = Image.new("RGB", (ancho_img, alto_img), "white")
        draw = ImageDraw.Draw(imagen)

        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        radio = 30
        y_gap = 200
        x_gap = 250
        self.posiciones = {}

        for gen_idx, gen in enumerate(sorted(generaciones.keys())):
            personas = generaciones[gen]
            y = 80 + gen_idx * y_gap
            total = len(personas)
            ancho_total = total * x_gap
            # Centrar horizontalmente pero permitir scroll
            x_start = (ancho_img - ancho_total) / 2 + x_gap / 2

            for i, p in enumerate(personas):
                x = x_start + i * x_gap
                outline = "gray" if p["fallecido"] else "red" if p["genero"] == "F" else "blue"
                text_fill = "gray" if p["fallecido"] else "black"

                draw.ellipse([x - radio, y - radio, x + radio, y + radio], outline=outline, width=3, fill="white")

                nombre_corto = p["nombre"].split()[0]
                text = f"{nombre_corto}\n{p['edad']} años"
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                except:
                    tw, th = draw.textsize(text, font=font)
                draw.text((x - tw // 2, y + radio + 8), text, fill=text_fill, font=font)

                self.posiciones[p["cedula"]] = (x, y)

        self._dibujar_conexiones(draw, radio)

        self.img_tk = ImageTk.PhotoImage(imagen)
        self.canvas.delete("all")
        # Configurar scrollregion para permitir scroll horizontal y vertical
        self.canvas.config(scrollregion=(0, 0, ancho_img, alto_img))
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)
        self.canvas.update_idletasks()
        self._dibujo_listo = True

    def _dibujar_conexiones(self, draw, radio):
        """Dibuja todas las conexiones con arcos inteligentes que evitan superposición"""

        # Definir colores por tipo de relación
        colores = {
            "padre_hijo": "gray",  # Gris
            "matrimonio": "purple",  # Púrpura
            "hermanos": "#FF8C00",  # Naranja
            "tios": "#0066CC",  # Azul
            "abuelos": "#9932CC",  # Violeta
        }

        # Recolectar todas las conexiones usando listas optimizadas
        conexiones_basicas = []  # Para padres, hermanos, tíos, abuelos
        matrimonios = []  # Para matrimonios (con tratamiento especial)

        # Padre → hijo (arcos hacia abajo)
        for p in self.personas.values():
            if p["cedula"] not in self.posiciones:
                continue
            x1, y1 = self.posiciones[p["cedula"]]

            for i, hijo_ced in enumerate(p["hijos"]):
                if hijo_ced in self.posiciones:
                    x2, y2 = self.posiciones[hijo_ced]
                    # Offset horizontal para evitar superposición
                    offset_x = i * 4 - 2  # -2, 0, 2, 4...
                    conexiones_basicas.append({
                        "tipo": "padre_hijo",
                        "p1": (x1 + offset_x, y1 + radio),
                        "p2": (x2 + offset_x, y2 - radio),
                        "color": colores["padre_hijo"],
                        "width": 2,
                        "curvatura": 15
                    })

        # Matrimonios (arcos inteligentes)
        parejas_procesadas = set()
        for p in self.personas.values():
            if p["pareja"] and p["pareja"] in self.posiciones:
                key = tuple(sorted([p["cedula"], p["pareja"]]))
                if key in parejas_procesadas:
                    continue
                parejas_procesadas.add(key)

                x1, y1 = self.posiciones[p["cedula"]]
                x2, y2 = self.posiciones[p["pareja"]]

                # Solo dibujar si están relativamente cerca verticalmente
                if abs(y1 - y2) < 100:
                    matrimonios.append({
                        "p1": (x1 + radio, y1),
                        "p2": (x2 - radio, y2),
                        "color": colores["matrimonio"],
                        "width": 3
                    })

        # Hermanos (arcos suaves)
        hermanos_procesados = set()
        for p in self.personas.values():
            for hermano_ced in p["hermanos"]:
                if hermano_ced in self.posiciones:
                    key = tuple(sorted([p["cedula"], hermano_ced]))
                    if key in hermanos_procesados:
                        continue
                    hermanos_procesados.add(key)

                    x1, y1 = self.posiciones[p["cedula"]]
                    x2, y2 = self.posiciones[hermano_ced]
                    if abs(y1 - y2) < 50:
                        conexiones_basicas.append({
                            "tipo": "hermanos",
                            "p1": (x1 + radio, y1),
                            "p2": (x2 - radio, y2),
                            "color": colores["hermanos"],
                            "width": 2,
                            "curvatura": 10
                        })

        # Tíos (arcos con curvatura diferente)
        tios_procesados = set()
        for p in self.personas.values():
            for padre_ced in p["padres"]:
                if padre_ced in self.personas:
                    padre = self.personas[padre_ced]
                    for hermano_padre_ced in padre["hermanos"]:
                        if hermano_padre_ced in self.posiciones:
                            key = tuple(sorted([p["cedula"], hermano_padre_ced]))
                            if key in tios_procesados:
                                continue
                            tios_procesados.add(key)

                            x1, y1 = self.posiciones[p["cedula"]]
                            x2, y2 = self.posiciones[hermano_padre_ced]
                            conexiones_basicas.append({
                                "tipo": "tios",
                                "p1": (x1, y1),
                                "p2": (x2, y2),
                                "color": colores["tios"],
                                "width": 1,
                                "curvatura": 25
                            })

        # Abuelos (arcos suaves)
        abuelos_procesados = set()
        for p in self.personas.values():
            for padre_ced in p["padres"]:
                if padre_ced in self.personas:
                    for abuelo_ced in self.personas[padre_ced]["padres"]:
                        if abuelo_ced in self.posiciones:
                            key = tuple(sorted([p["cedula"], abuelo_ced]))
                            if key in abuelos_procesados:
                                continue
                            abuelos_procesados.add(key)

                            x1, y1 = self.posiciones[p["cedula"]]
                            x2, y2 = self.posiciones[abuelo_ced]
                            conexiones_basicas.append({
                                "tipo": "abuelos",
                                "p1": (x1, y1),
                                "p2": (x2, y2),
                                "color": colores["abuelos"],
                                "width": 1,
                                "curvatura": 20
                            })

        # Dibujar conexiones básicas (arcos)
        for conn in conexiones_basicas:
            self._dibujar_arco(draw, conn["p1"], conn["p2"], conn["color"], conn["width"], conn["curvatura"])

        # Dibujar matrimonios (arcos inteligentes)
        for mat in matrimonios:
            self._dibujar_arco_matrimonio(draw, mat["p1"], mat["p2"], mat["color"], mat["width"])

    def _dibujar_arco_matrimonio(self, draw, punto1, punto2, fill, width):
        """Dibuja un arco de matrimonio que evita pasar por encima de otras personas"""
        x1, y1 = punto1
        x2, y2 = punto2

        # Calcular punto medio
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        # Calcular altura del arco basada en la distancia horizontal
        distancia_horizontal = abs(x2 - x1)
        altura_arco = max(30, min(80, distancia_horizontal / 8))  # Entre 30 y 80 píxeles

        # Punto de control para el arco (arriba para que no pase por personas)
        control_x = mx
        control_y = my - altura_arco  # Arco hacia arriba

        # Verificar si hay personas en el camino del arco
        personas_en_camino = []
        for p in self.personas.values():
            if p["cedula"] in self.posiciones:
                px, py = self.posiciones[p["cedula"]]
                # Verificar si la persona está cerca de la trayectoria del arco
                if (min(x1, x2) - 20 <= px <= max(x1, x2) + 20 and
                        control_y - 30 <= py <= my + 30):
                    personas_en_camino.append((px, py))

        # Si hay personas en el camino, ajustar la altura del arco
        if personas_en_camino:
            # Encontrar la persona más alta en el camino
            persona_mas_alta = min(personas_en_camino, key=lambda pos: pos[1])
            altura_arco = max(altura_arco, (my - persona_mas_alta[1]) + 40)
            control_y = my - altura_arco

        # Crear puntos del arco usando curva cuadrática de Bézier
        puntos = []
        num_segmentos = 35  # Alta calidad para matrimonios

        for i in range(num_segmentos + 1):
            t = i / num_segmentos
            # Fórmula de Bézier cuadrática
            xt = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * control_x + t ** 2 * x2
            yt = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * control_y + t ** 2 * y2
            puntos.append((xt, yt))

        # Dibujar segmentos de línea que forman el arco
        for i in range(len(puntos) - 1):
            draw.line([puntos[i], puntos[i + 1]], fill=fill, width=width)

    def _dibujar_arco(self, draw, punto1, punto2, fill, width, curvatura):
        """Dibuja un arco suave entre dos puntos usando segmentos de línea"""
        x1, y1 = punto1
        x2, y2 = punto2

        # Calcular punto medio
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        # Calcular punto de control para el arco
        if abs(y1 - y2) < 20:  # Casi horizontal - arco hacia abajo
            control_x = mx
            control_y = my + curvatura
        else:  # Vertical o diagonal - arco lateral
            control_x = mx + curvatura
            control_y = my

        # Crear puntos del arco usando curva cuadrática de Bézier
        puntos = []
        num_segmentos = 25  # Buena calidad para conexiones básicas

        for i in range(num_segmentos + 1):
            t = i / num_segmentos
            # Fórmula de Bézier cuadrática
            xt = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * control_x + t ** 2 * x2
            yt = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * control_y + t ** 2 * y2
            puntos.append((xt, yt))

        # Dibujar segmentos de línea que forman el arco
        for i in range(len(puntos) - 1):
            draw.line([puntos[i], puntos[i + 1]], fill=fill, width=width)