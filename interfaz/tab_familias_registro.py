# interfaz/tab_familias_registro.py
import tkinter as tk
from tkinter import ttk, messagebox

class TabFamiliasRegistro:
    def __init__(self, parent, gestor_familias):
        self.parent = parent
        self.gestor = gestor_familias
        self.frame = ttk.Frame(parent)
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        ttk.Label(main_frame, text="Gestión de Familias", 
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Formulario para nueva familia
        form_frame = ttk.LabelFrame(main_frame, text="Registrar Nueva Familia")
        form_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(form_frame, text="Nombre de la familia:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.nombre_entry = ttk.Entry(form_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=10)
        self.nombre_entry.bind('<Return>', lambda e: self.registrar_familia())

        ttk.Button(form_frame, text="Registrar Familia", 
                  command=self.registrar_familia).grid(row=0, column=2, padx=10, pady=10)

        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Familias Registradas")
        results_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Treeview para mostrar familias
        columns = ('ID', 'Nombre', 'Miembros', 'Fecha')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Definir encabezados
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Miembros', text='Miembros')
        self.tree.heading('Fecha', text='Fecha Creación')
        
        # Definir ancho de columnas
        self.tree.column('ID', width=80)
        self.tree.column('Nombre', width=200)
        self.tree.column('Miembros', width=80)
        self.tree.column('Fecha', width=120)
        
        # Scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Botón para refrescar
        ttk.Button(main_frame, text="Actualizar Lista", 
                  command=self.cargar_familias).pack(pady=10)
        
        # Cargar familias al iniciar
        self.cargar_familias()

    def registrar_familia(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese el nombre de la familia")
            return
        
        try:
            familia_id = self.gestor.insertar_familia(nombre)
            messagebox.showinfo("Éxito", f"Familia registrada con ID: {familia_id}")
            self.nombre_entry.delete(0, tk.END)
            self.cargar_familias()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar familia: {e}")

    def cargar_familias(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar familias
        try:
            familias = self.gestor.listar_familias()
            for familia in familias:
                self.tree.insert('', tk.END, values=(
                    familia['id'],
                    familia['nombre'],
                    len(familia['miembros']),
                    familia['fecha_creacion']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar familias: {e}")