# interfaz/tab_arbol.py
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from arbol.generador_arbol import GeneradorArbol

class TabArbol:
    def __init__(self, parent, interfaz_principal):
        self.parent = parent
        self.interfaz = interfaz_principal
        self.frame = ttk.Frame(parent)
        self.generador_arbol = GeneradorArbol()
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Búsqueda ---
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Persona")
        search_frame.pack(fill="x", pady=5)

        ttk.Label(search_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.nombre_entry = ttk.Entry(search_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        self.nombre_entry.bind('<KeyRelease>', self.buscar_nombres)

        ttk.Button(search_frame, text="Buscar", command=self.buscar_personas).grid(row=0, column=2, padx=5, pady=5)

        # --- Resultados ---
        results_frame = ttk.LabelFrame(main_frame, text="Resultados")
        results_frame.pack(fill="both", expand=True, pady=5)

        self.result_listbox = tk.Listbox(results_frame, height=8)
        self.result_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.result_listbox.bind('<Double-1>', self.seleccionar_persona)

        scrollbar = ttk.Scrollbar(self.result_listbox)
        scrollbar.pack(side="right", fill="y")
        self.result_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_listbox.yview)

        # --- Información ---
        info_frame = ttk.LabelFrame(main_frame, text="Información de la Persona")
        info_frame.pack(fill="x", pady=5)

        self.info_text = tk.Text(info_frame, height=12, wrap="word")
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Botón Árbol ---
        ttk.Button(main_frame, text="Mostrar Árbol Familiar", command=self.mostrar_arbol).pack(pady=5)

        # --- Área del gráfico ---
        self.fig_frame = ttk.Frame(main_frame)
        self.fig_frame.pack(fill="both", expand=True, pady=5)

    def buscar_nombres(self, event=None):
        termino = self.nombre_entry.get().strip().lower()
        if len(termino) < 2:
            self.result_listbox.delete(0, tk.END)
            return
        resultados = [f"{n} (Cédula: {c})" for c, n in self.interfaz.personas_lista if termino in n.lower()][:20]
        self.result_listbox.delete(0, tk.END)
        for item in resultados:
            self.result_listbox.insert(tk.END, item)

    def buscar_personas(self):
        self.buscar_nombres()

    def seleccionar_persona(self, event=None):
        selection = self.result_listbox.curselection()
        if not selection:
            return
        item = self.result_listbox.get(selection[0])
        try:
            cedula = item.split("(Cédula: ")[1].split(")")[0]
            self.interfaz.cedula_seleccionada = cedula
            self.mostrar_informacion_persona(cedula)
        except:
            messagebox.showerror("Error", "No se pudo extraer la cédula.")

    def mostrar_informacion_persona(self, cedula):
        if cedula not in self.interfaz.datos:
            messagebox.showerror("Error", "Persona no encontrada.")
            return
        datos = self.interfaz.datos[cedula]
        relaciones = datos["relaciones"]
        info = f"Nombre: {datos['nombre']}\nCédula: {cedula}\nGeneración: {relaciones['generacion']}\n\nRelaciones:\n"
        relaciones_mostrar = [
            ("Padres", "padres"), ("Hijos", "hijos"), ("Pareja", "pareja"),
            ("Hermanos", "hermanos"), ("Abuelos", "abuelos"), ("Tíos", "tios"),
            ("Sobrinos", "sobrinos"), ("Primos", "primos")
        ]
        for nombre, clave in relaciones_mostrar:
            valor = relaciones[clave]
            if isinstance(valor, list):
                nombres = [self.interfaz.datos.get(id, {}).get("nombre", id) for id in valor[:5]]
                info += f"{nombre}: {', '.join(nombres) if nombres else 'Ninguno'}\n"
            elif valor:
                info += f"{nombre}: {self.interfaz.datos.get(valor, {}).get('nombre', valor)}\n"
            else:
                info += f"{nombre}: Ninguno\n"
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)

    def mostrar_arbol(self):
        if not self.interfaz.cedula_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una persona primero.")
            return
        cedula = self.interfaz.cedula_seleccionada
        
        for widget in self.fig_frame.winfo_children():
            widget.destroy()

        # Generar y mostrar el árbol
        fig = self.generador_arbol.crear_arbol_familiar(
            cedula, 
            self.interfaz.datos, 
            self.interfaz.datos[cedula]['nombre']
        )
        
        if fig:
            canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)