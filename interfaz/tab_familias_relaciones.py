# interfaz/tab_familias_relaciones.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

class TabFamiliasRelaciones:
    def __init__(self, parent, gestor_familias, interfaz_principal):
        self.parent = parent
        self.gestor = gestor_familias
        self.interfaz = interfaz_principal
        self.frame = ttk.Frame(parent)
        self.personas_cache = {}  # Cache para evitar recargas frecuentes
        self.crear_widgets()
        self.actualizar_lista_personas()

    def crear_widgets(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        ttk.Label(main_frame, text="Gestión de Relaciones Familiares", 
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Panel principal
        panel_frame = ttk.Frame(main_frame)
        panel_frame.pack(fill="both", expand=True, pady=10)

        # === Panel izquierdo: Selección de personas ===
        left_frame = ttk.LabelFrame(panel_frame, text="Selección de Personas")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        # Persona 1
        p1_frame = ttk.LabelFrame(left_frame, text="Persona 1")
        p1_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(p1_frame, text="Seleccionar:").pack(anchor="w", padx=5, pady=2)
        self.persona1_var = tk.StringVar()
        self.persona1_combo = ttk.Combobox(p1_frame, textvariable=self.persona1_var, 
                                          state="readonly", width=40)
        self.persona1_combo.pack(fill="x", padx=5, pady=5)

        # Persona 2 (opcional para algunas relaciones)
        p2_frame = ttk.LabelFrame(left_frame, text="Persona 2")
        p2_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(p2_frame, text="Seleccionar:").pack(anchor="w", padx=5, pady=2)
        self.persona2_var = tk.StringVar()
        self.persona2_combo = ttk.Combobox(p2_frame, textvariable=self.persona2_var, 
                                          state="readonly", width=40)
        self.persona2_combo.pack(fill="x", padx=5, pady=5)

        # Botón para agregar más personas (para hermanos)
        self.btn_agregar_persona = ttk.Button(left_frame, text="Agregar Persona", 
                                             command=self.agregar_persona_adicional,
                                             state="disabled")
        self.btn_agregar_persona.pack(pady=10)

        # === Panel derecho: Tipo de relación ===
        right_frame = ttk.LabelFrame(panel_frame, text="Tipo de Relación")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        # Tipo de relación
        ttk.Label(right_frame, text="Relación:").pack(anchor="w", padx=5, pady=2)
        self.tipo_relacion_var = tk.StringVar()
        self.tipo_relacion_combo = ttk.Combobox(right_frame, 
                                               textvariable=self.tipo_relacion_var,
                                               values=["Padre/Hijo", "Hermanos", "Pareja"],
                                               state="readonly", width=30)
        self.tipo_relacion_combo.pack(fill="x", padx=5, pady=5)
        self.tipo_relacion_combo.bind('<<ComboboxSelected>>', self.on_tipo_relacion_change)

        # Subtipo (biológico/adoptivo, etc.)
        self.subtipo_frame = ttk.LabelFrame(right_frame, text="Detalles")
        self.subtipo_frame.pack(fill="x", padx=10, pady=10)

        self.subtipo_var = tk.StringVar()
        self.subtipo_combo = ttk.Combobox(self.subtipo_frame, 
                                         textvariable=self.subtipo_var,
                                         state="readonly", width=30)
        self.subtipo_combo.pack(fill="x", padx=5, pady=5)

        # Área de personas adicionales (para hermanos)
        self.personas_adicionales_frame = ttk.LabelFrame(right_frame, text="Personas Adicionales")
        self.personas_adicionales_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.personas_adicionales_frame.pack_forget()  # Oculto por defecto

        self.personas_adicionales_listbox = tk.Listbox(self.personas_adicionales_frame, height=4)
        self.personas_adicionales_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        # Vincular evento de selección en la lista
        self.personas_adicionales_listbox.bind('<<ListboxSelect>>', self.on_lista_seleccion)

        # Botón de eliminar persona adicional
        self.btn_eliminar_persona = ttk.Button(self.personas_adicionales_frame, 
                                              text="Eliminar Seleccionada",
                                              command=self.eliminar_persona_adicional,
                                              state="disabled")
        self.btn_eliminar_persona.pack(pady=5)

        # Botón de registro
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=20)

        self.btn_registrar = ttk.Button(btn_frame, text="Registrar Relación", 
                                       command=self.registrar_relacion,
                                       style="Accent.TButton")
        self.btn_registrar.pack(pady=10)

        # Área de información
        info_frame = ttk.LabelFrame(main_frame, text="Información")
        info_frame.pack(fill="x", pady=10)

        self.info_text = tk.Text(info_frame, height=6, wrap="word")
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.info_text.insert("1.0", "Seleccione personas y el tipo de relación para comenzar.\n"
                           "El sistema registrará automáticamente las relaciones recíprocas.")

        # Inicializar valores por defecto
        self.tipo_relacion_var.set("Padre/Hijo")
        self.on_tipo_relacion_change()

    def on_tipo_relacion_change(self, event=None):
        """Maneja el cambio en el tipo de relación"""
        tipo = self.tipo_relacion_var.get()
        
        # Limpiar selecciones
        self.persona1_var.set("")
        self.persona2_var.set("")
        
        # Configurar subtipos según el tipo de relación
        if tipo == "Padre/Hijo":
            self.subtipo_combo['values'] = ["Biológico", "Adoptivo"]
            self.subtipo_var.set("Biológico")
            self.btn_agregar_persona.config(state="disabled")
            self.personas_adicionales_frame.pack_forget()
        elif tipo == "Hermanos":
            self.subtipo_combo['values'] = ["Biológicos", "Medios", "Adoptivos"]
            self.subtipo_var.set("Biológicos")
            self.btn_agregar_persona.config(state="normal")
            self.personas_adicionales_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.personas_adicionales_listbox.delete(0, tk.END)
            # Desactivar botón de eliminar al limpiar
            self.btn_eliminar_persona.config(state="disabled")
        elif tipo == "Pareja":
            self.subtipo_combo['values'] = ["Casados", "Unión Libre"]
            self.subtipo_var.set("Casados")
            self.btn_agregar_persona.config(state="disabled")
            self.personas_adicionales_frame.pack_forget()

    def on_lista_seleccion(self, event=None):
        """Maneja la selección en la lista de personas adicionales"""
        # Activar el botón de eliminar si hay una selección
        if self.personas_adicionales_listbox.curselection():
            self.btn_eliminar_persona.config(state="normal")
        else:
            self.btn_eliminar_persona.config(state="disabled")

    def actualizar_lista_personas(self):
        """Actualiza las listas de personas disponibles"""
        try:
            # Obtener todas las personas del gestor de familias
            familias = self.gestor.listar_familias()
            personas = []
            
            for familia in familias:
                for miembro in familia.get("miembros", []):
                    cedula = miembro.get("cedula", "")
                    nombre = miembro.get("nombre", "")
                    if cedula and nombre:
                        personas.append(f"{cedula} - {nombre}")
            
            # Actualizar comboboxes
            self.persona1_combo['values'] = personas
            self.persona2_combo['values'] = personas
            
            # Guardar en cache
            self.personas_cache = {p.split(" - ")[0]: p for p in personas}
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar personas: {e}")

    def agregar_persona_adicional(self):
        """Agrega una persona adicional para relaciones de hermandad"""
        persona_seleccionada = self.persona2_var.get()
        if not persona_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una persona primero")
            return
            
        # Verificar que no esté ya en la lista
        personas_existentes = self.personas_adicionales_listbox.get(0, tk.END)
        if persona_seleccionada in personas_existentes:
            messagebox.showwarning("Advertencia", "Esta persona ya está en la lista")
            return
            
        # Agregar a la lista
        self.personas_adicionales_listbox.insert(tk.END, persona_seleccionada)
        self.persona2_var.set("")  # Limpiar selección

    def eliminar_persona_adicional(self):
        """Elimina una persona seleccionada de la lista adicional"""
        seleccion = self.personas_adicionales_listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una persona para eliminar")
            return
            
        self.personas_adicionales_listbox.delete(seleccion[0])
        # Desactivar botón después de eliminar
        self.btn_eliminar_persona.config(state="disabled")

    def registrar_relacion(self):
        """Registra la relación seleccionada"""
        try:
            tipo_relacion = self.tipo_relacion_var.get()
            
            if tipo_relacion == "Padre/Hijo":
                self._registrar_padre_hijo()
            elif tipo_relacion == "Hermanos":
                self._registrar_hermanos()
            elif tipo_relacion == "Pareja":
                self._registrar_pareja()
                
            # Actualizar árbol genealógico
            self.actualizar_arbol_genealogico()
            
            messagebox.showinfo("Éxito", "Relación registrada correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar relación: {str(e)}")

    def _registrar_padre_hijo(self):
        """Registra una relación padre/hijo"""
        persona1 = self.persona1_var.get()
        persona2 = self.persona2_var.get()
        
        if not persona1 or not persona2:
            raise ValueError("Debe seleccionar ambas personas")
        
        # Extraer cédulas (que son los IDs en tu sistema)
        cedula_padre = persona1.split(" - ")[0]
        cedula_hijo = persona2.split(" - ")[0]
        
        # Determinar tipo
        tipo = "biológico" if self.subtipo_var.get() == "Biológico" else "adoptivo"
        
        # Registrar relación usando el método existente
        try:
            self.gestor.registrar_hijo(cedula_padre, cedula_hijo, tipo)
        except Exception as e:
            raise Exception(f"Error al registrar padre-hijo: {str(e)}")

    def _registrar_hermanos(self):
        """Registra relaciones de hermandad"""
        persona1 = self.persona1_var.get()
        if not persona1:
            raise ValueError("Debe seleccionar la primera persona")
        
        # Obtener todas las personas (persona1 + adicionales)
        personas_seleccionadas = [persona1]
        for i in range(self.personas_adicionales_listbox.size()):
            personas_seleccionadas.append(self.personas_adicionales_listbox.get(i))
        
        if len(personas_seleccionadas) < 2:
            raise ValueError("Debe seleccionar al menos 2 personas para registrar hermandad")
        
        # Extraer cédulas
        cedulas = [p.split(" - ")[0] for p in personas_seleccionadas]
        
        # Registrar hermandad usando el método existente
        try:
            self.gestor.registrar_hermanos(cedulas)
        except Exception as e:
            raise Exception(f"Error al registrar hermandad: {str(e)}")

    def _registrar_pareja(self):
        """Registra una relación de pareja"""
        persona1 = self.persona1_var.get()
        persona2 = self.persona2_var.get()
        
        if not persona1 or not persona2:
            raise ValueError("Debe seleccionar ambas personas")
        
        # Extraer cédulas
        cedula1 = persona1.split(" - ")[0]
        cedula2 = persona2.split(" - ")[0]
        
        # Determinar tipo de unión
        tipo = "casado" if self.subtipo_var.get() == "Casados" else "unión libre"
        
        # Registrar relación usando el método existente
        try:
            self.gestor.registrar_pareja(cedula1, cedula2, tipo)
        except Exception as e:
            raise Exception(f"Error al registrar pareja: {str(e)}")

    def actualizar_arbol_genealogico(self):
        """Actualiza el árbol genealógico en la interfaz"""
        try:
            # Recargar datos
            self.interfaz.cargar_datos()
            
            # Si hay una persona seleccionada en el árbol, actualizar su vista
            if hasattr(self.interfaz, 'tab_arbol') and self.interfaz.cedula_seleccionada:
                self.interfaz.tab_arbol.mostrar_informacion_persona(self.interfaz.cedula_seleccionada)
                self.interfaz.tab_arbol.mostrar_arbol()
            
        except Exception as e:
            messagebox.showwarning("Advertencia", f"No se pudo actualizar el árbol: {e}")