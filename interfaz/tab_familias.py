# interfaz/tab_familias.py
import tkinter as tk
from tkinter import ttk
from interfaz.tab_familias_registro import TabFamiliasRegistro
from interfaz.tab_familias_integrantes import TabFamiliasIntegrantes
from interfaz.tab_familias_relaciones import TabFamiliasRelaciones

class TabFamilias:
    def __init__(self, parent, interfaz_principal):
        self.parent = parent
        self.interfaz = interfaz_principal
        self.frame = ttk.Frame(parent)
        self.gestor = interfaz_principal.gestor_familias  # AHORA SÍ EXISTE
        self.crear_widgets()

    def crear_widgets(self):
        # Notebook para separar registro de familias e integrantes
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña 1: Registro de familias
        self.tab_registro = TabFamiliasRegistro(self.notebook, self.gestor)
        self.notebook.add(self.tab_registro.frame, text="Registro de Familias")

        # Pestaña 2: Gestión de integrantes
        self.tab_integrantes = TabFamiliasIntegrantes(self.notebook, self.gestor)
        self.notebook.add(self.tab_integrantes.frame, text="Gestión de Integrantes")

        # Pestaña 3: Gestión de relaciones (NUEVA)
        self.tab_relaciones = TabFamiliasRelaciones(self.notebook, self.gestor, self.interfaz)
        self.notebook.add(self.tab_relaciones.frame, text="Gestión de Relaciones")