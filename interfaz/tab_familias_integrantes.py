# interfaz/tab_familias_integrantes.py
import tkinter as tk
from tkinter import ttk, messagebox

class TabFamiliasIntegrantes:
    def __init__(self, parent, gestor_familias):
        self.parent = parent
        self.gestor = gestor_familias
        self.frame = ttk.Frame(parent)
        
        # Datos para los menús desplegables
        self.generos = ["Masculino", "Femenino", "No especificado"]
        self.provincias = [
            "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", 
            "Puntarenas", "Limón", "No especificado"
        ]
        self.estados_civiles = [
            "Soltero", "Casado", "Divorciado", "Viudo", "Unión Libre", 
            "Separado", "No especificado"
        ]
        
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Selección de familia
        select_frame = ttk.LabelFrame(main_frame, text="Seleccionar Familia")
        select_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(select_frame, text="Familia:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.familia_var = tk.StringVar()
        self.familia_combo = ttk.Combobox(select_frame, textvariable=self.familia_var, width=50, state="readonly")
        self.familia_combo.grid(row=0, column=1, padx=5, pady=10)
        self.familia_combo.bind('<<ComboboxSelected>>', self.cargar_miembros_familia)

        ttk.Button(select_frame, text="Actualizar Lista", 
                  command=self.actualizar_lista_familias).grid(row=0, column=2, padx=10, pady=10)

        # Formulario para nuevo miembro
        form_frame = ttk.LabelFrame(main_frame, text="Registrar Nuevo Miembro")
        form_frame.pack(fill="x", pady=10, padx=10)

        # Primera fila
        ttk.Label(form_frame, text="Cédula:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cedula_entry = ttk.Entry(form_frame, width=15)
        self.cedula_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.nombre_entry_miembro = ttk.Entry(form_frame, width=30)
        self.nombre_entry_miembro.grid(row=0, column=3, padx=5, pady=5)

        # Segunda fila
        ttk.Label(form_frame, text="Fecha Nacimiento (AAAA-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fecha_nac_entry = ttk.Entry(form_frame, width=15)
        self.fecha_nac_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Fecha Fallecimiento (opcional):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.fecha_fall_entry = ttk.Entry(form_frame, width=15)
        self.fecha_fall_entry.grid(row=1, column=3, padx=5, pady=5)

        # Tercera fila - Menús desplegables
        ttk.Label(form_frame, text="Género:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.genero_var = tk.StringVar(value="No especificado")
        self.genero_combo = ttk.Combobox(form_frame, textvariable=self.genero_var, 
                                        values=self.generos, state="readonly", width=15)
        self.genero_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Provincia:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.provincia_var = tk.StringVar(value="No especificado")
        self.provincia_combo = ttk.Combobox(form_frame, textvariable=self.provincia_var, 
                                           values=self.provincias, state="readonly", width=20)
        self.provincia_combo.grid(row=2, column=3, padx=5, pady=5)

        # Cuarta fila
        ttk.Label(form_frame, text="Estado Civil:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.estado_civil_var = tk.StringVar(value="No especificado")
        self.estado_civil_combo = ttk.Combobox(form_frame, textvariable=self.estado_civil_var, 
                                              values=self.estados_civiles, state="readonly", width=20)
        self.estado_civil_combo.grid(row=3, column=1, padx=5, pady=5)

        # Botones de acción
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=3, column=3, padx=10, pady=10)

        ttk.Button(buttons_frame, text="Registrar Miembro", 
                  command=self.registrar_miembro).pack(side="left", padx=2)
        ttk.Button(buttons_frame, text="Editar Miembro", 
                  command=self.editar_miembro).pack(side="left", padx=2)
        ttk.Button(buttons_frame, text="Eliminar Miembro", 
                  command=self.eliminar_miembro).pack(side="left", padx=2)

        # Área de miembros
        members_frame = ttk.LabelFrame(main_frame, text="Miembros de la Familia")
        members_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Treeview para mostrar miembros
        member_columns = ('Cédula', 'Nombre', 'Nacimiento', 'Fallecimiento', 'Género', 'Provincia', 'Estado Civil')
        self.members_tree = ttk.Treeview(members_frame, columns=member_columns, show='headings', height=10)
        
        # Definir encabezados
        for col in member_columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=100)
        
        # Scrollbars
        vsb_members = ttk.Scrollbar(members_frame, orient="vertical", command=self.members_tree.yview)
        hsb_members = ttk.Scrollbar(members_frame, orient="horizontal", command=self.members_tree.xview)
        self.members_tree.configure(yscrollcommand=vsb_members.set, xscrollcommand=hsb_members.set)
        
        # Vincular evento de selección en el treeview
        self.members_tree.bind("<<TreeviewSelect>>", self.on_seleccionar_miembro)
        
        # Grid layout
        self.members_tree.grid(row=0, column=0, sticky='nsew')
        vsb_members.grid(row=0, column=1, sticky='ns')
        hsb_members.grid(row=1, column=0, sticky='ew')
        
        members_frame.grid_rowconfigure(0, weight=1)
        members_frame.grid_columnconfigure(0, weight=1)

        # Cargar lista de familias
        self.actualizar_lista_familias()

    def on_seleccionar_miembro(self, event=None):
        """Maneja la selección de un miembro en el treeview"""
        seleccion = self.members_tree.selection()
        if seleccion:
            # Obtener los valores del elemento seleccionado
            item = self.members_tree.item(seleccion[0])
            valores = item['values']
            
            # Rellenar el formulario con los datos seleccionados
            self.cedula_entry.delete(0, tk.END)
            self.cedula_entry.insert(0, valores[0] if valores[0] else "")
            
            self.nombre_entry_miembro.delete(0, tk.END)
            self.nombre_entry_miembro.insert(0, valores[1] if valores[1] else "")
            
            self.fecha_nac_entry.delete(0, tk.END)
            self.fecha_nac_entry.insert(0, valores[2] if valores[2] else "")
            
            self.fecha_fall_entry.delete(0, tk.END)
            self.fecha_fall_entry.insert(0, valores[3] if valores[3] else "")
            
            # Establecer valores en comboboxes
            genero = valores[4] if valores[4] else "No especificado"
            if genero in self.generos:
                self.genero_var.set(genero)
            else:
                self.genero_var.set("No especificado")
                
            provincia = valores[5] if valores[5] else "No especificado"
            if provincia in self.provincias:
                self.provincia_var.set(provincia)
            else:
                self.provincia_var.set("No especificado")
                
            estado_civil = valores[6] if valores[6] else "No especificado"
            if estado_civil in self.estados_civiles:
                self.estado_civil_var.set(estado_civil)
            else:
                self.estado_civil_var.set("No especificado")

    def actualizar_lista_familias(self):
        """Actualiza la lista de familias en el combobox de integrantes"""
        try:
            familias = self.gestor.listar_familias()
            familia_options = [f"{f['id']} - {f['nombre']}" for f in familias]
            self.familia_combo['values'] = familia_options
            
            if familia_options:
                self.familia_combo.set(familia_options[0])
                self.cargar_miembros_familia()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar lista de familias: {e}")

    def registrar_miembro(self):
        # Validar selección de familia
        familia_seleccionada = self.familia_var.get()
        if not familia_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una familia")
            return
        
        # Extraer ID de la familia
        try:
            familia_id = familia_seleccionada.split(" - ")[0]
        except:
            messagebox.showerror("Error", "Formato de familia inválido")
            return

        # Obtener datos del formulario
        cedula = self.cedula_entry.get().strip()
        nombre = self.nombre_entry_miembro.get().strip()
        fecha_nac = self.fecha_nac_entry.get().strip()
        fecha_fall = self.fecha_fall_entry.get().strip() or None
        genero = self.genero_var.get()
        provincia = self.provincia_var.get()
        estado_civil = self.estado_civil_var.get()

        # Validaciones básicas
        if not cedula or not nombre or not fecha_nac:
            messagebox.showwarning("Advertencia", "Cédula, nombre y fecha de nacimiento son obligatorios")
            return

        try:
            miembro = self.gestor.insertar_miembro(
                familia_id, cedula, nombre, fecha_nac, fecha_fall,
                genero, provincia, estado_civil
            )
            messagebox.showinfo("Éxito", "Miembro registrado correctamente")
            
            # Limpiar formulario
            self.limpiar_formulario_miembro()
            
            # Recargar lista de miembros
            self.cargar_miembros_familia()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar miembro: {e}")

    def editar_miembro(self):
        """Edita un miembro existente"""
        # Validar selección de familia
        familia_seleccionada = self.familia_var.get()
        if not familia_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una familia")
            return
            
        # Verificar que haya una selección en el treeview
        seleccion = self.members_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un miembro para editar")
            return
            
        # Extraer ID de la familia
        try:
            familia_id = familia_seleccionada.split(" - ")[0]
        except:
            messagebox.showerror("Error", "Formato de familia inválido")
            return

        # Obtener datos del formulario
        cedula = self.cedula_entry.get().strip()
        nombre = self.nombre_entry_miembro.get().strip()
        fecha_nac = self.fecha_nac_entry.get().strip()
        fecha_fall = self.fecha_fall_entry.get().strip() or None
        genero = self.genero_var.get()
        provincia = self.provincia_var.get()
        estado_civil = self.estado_civil_var.get()

        # Validaciones básicas
        if not cedula or not nombre or not fecha_nac:
            messagebox.showwarning("Advertencia", "Cédula, nombre y fecha de nacimiento son obligatorios")
            return
            
        # Verificar que la cédula no haya cambiado (esto es importante para la identificación)
        item = self.members_tree.item(seleccion[0])
        cedula_original = str(item['values'][0]).strip()  # Convertir a string y eliminar espacios
        cedula_a_comparar = cedula.strip()  # Eliminar espacios de la cédula del formulario
        
        if cedula_a_comparar != cedula_original:
            messagebox.showwarning("Advertencia", "No se puede cambiar la cédula de un miembro existente. Para cambiar la cédula, elimine y vuelva a crear el miembro.")
            return

        try:
            # Actualizar el miembro existente
            self._actualizar_miembro_en_familia(familia_id, cedula_a_comparar, nombre, fecha_nac, fecha_fall, genero, provincia, estado_civil)
            messagebox.showinfo("Éxito", "Miembro actualizado correctamente")
            
            # Limpiar formulario
            self.limpiar_formulario_miembro()
            
            # Recargar lista de miembros
            self.cargar_miembros_familia()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar miembro: {e}")

    def _actualizar_miembro_en_familia(self, familia_id, cedula, nombre, fecha_nac, fecha_fall, genero, provincia, estado_civil):
        """Actualiza los datos de un miembro en la familia"""
        # Obtener la familia
        familia = self.gestor.obtener_familia(familia_id)
        if not familia:
            raise ValueError("Familia no encontrada")
            
        # Buscar el miembro por cédula y actualizarlo
        for miembro in familia["miembros"]:
            if str(miembro.get("cedula")).strip() == cedula:
                # Extraer apellidos del nombre
                partes = nombre.strip().split()
                apellido1 = partes[1] if len(partes) > 1 else ""
                apellido2 = partes[2] if len(partes) > 2 else ""
                
                # Actualizar datos
                miembro["nombre"] = nombre
                miembro["apellido1"] = apellido1
                miembro["apellido2"] = apellido2
                miembro["fecha_nacimiento"] = fecha_nac
                miembro["fecha_fallecimiento"] = fecha_fall
                miembro["genero"] = genero
                miembro["lugar_residencia"] = provincia
                miembro["estado_civil"] = estado_civil
                miembro["fecha_actualizacion"] = self._obtener_fecha_actual()
                
                # Guardar cambios
                self.gestor._guardar_familias()
                return
                
        raise ValueError("Miembro no encontrado")

    def _obtener_fecha_actual(self):
        """Obtiene la fecha actual en formato YYYY-MM-DD"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def eliminar_miembro(self):
        """Elimina un miembro de la familia"""
        # Validar selección de familia
        familia_seleccionada = self.familia_var.get()
        if not familia_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una familia")
            return
            
        # Verificar que haya una selección en el treeview
        seleccion = self.members_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un miembro para eliminar")
            return
            
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este miembro?"):
            return
            
        # Extraer ID de la familia
        try:
            familia_id = familia_seleccionada.split(" - ")[0]
        except:
            messagebox.showerror("Error", "Formato de familia inválido")
            return
            
        # Obtener cédula del miembro seleccionado
        item = self.members_tree.item(seleccion[0])
        cedula = str(item['values'][0]).strip()
        
        try:
            # Eliminar el miembro de la familia
            self._eliminar_miembro_de_familia(familia_id, cedula)
            messagebox.showinfo("Éxito", "Miembro eliminado correctamente")
            
            # Limpiar formulario
            self.limpiar_formulario_miembro()
            
            # Recargar lista de miembros
            self.cargar_miembros_familia()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar miembro: {e}")

    def _eliminar_miembro_de_familia(self, familia_id, cedula):
        """Elimina un miembro de la familia por cédula"""
        # Obtener la familia
        familia = self.gestor.obtener_familia(familia_id)
        if not familia:
            raise ValueError("Familia no encontrada")
            
        # Buscar y eliminar el miembro por cédula
        for i, miembro in enumerate(familia["miembros"]):
            if str(miembro.get("cedula")).strip() == cedula:
                # Eliminar el miembro
                del familia["miembros"][i]
                familia["fecha_actualizacion"] = self._obtener_fecha_actual()
                
                # Guardar cambios
                self.gestor._guardar_familias()
                return
                
        raise ValueError("Miembro no encontrado")

    def cargar_miembros_familia(self, event=None):
        """Carga los miembros de la familia seleccionada"""
        # Limpiar treeview de miembros
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        familia_seleccionada = self.familia_var.get()
        if not familia_seleccionada:
            return
            
        try:
            familia_id = familia_seleccionada.split(" - ")[0]
            miembros = self.gestor.obtener_miembros(familia_id)
            
            for miembro in miembros:
                self.members_tree.insert('', tk.END, values=(
                    miembro.get('cedula', ''),
                    miembro.get('nombre', ''),
                    miembro.get('fecha_nacimiento', ''),
                    miembro.get('fecha_fallecimiento', '') or '',
                    miembro.get('genero', ''),
                    miembro.get('lugar_residencia', ''),
                    miembro.get('estado_civil', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar miembros: {e}")

    def limpiar_formulario_miembro(self):
        """Limpia el formulario de registro de miembros"""
        self.cedula_entry.delete(0, tk.END)
        self.nombre_entry_miembro.delete(0, tk.END)
        self.fecha_nac_entry.delete(0, tk.END)
        self.fecha_fall_entry.delete(0, tk.END)
        self.genero_var.set("No especificado")
        self.provincia_var.set("No especificado")
        self.estado_civil_var.set("No especificado")