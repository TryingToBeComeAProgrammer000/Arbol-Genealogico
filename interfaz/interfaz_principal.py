# interfaz/interfaz_principal.py
import tkinter as tk
from tkinter import ttk, messagebox
import json

from interfaz.tab_arbol import TabArbol
from interfaz.tab_consultas import TabConsultas
from interfaz.tab_familias import TabFamilias
from interfaz.tab_simulador import TabSimulador  # Nueva pestaña
from datos.gestor_datos import GestorDatos
from gestion_familias import GestorFamilias  # Gestor de familias


class InterfazFamiliar:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Familiar - Árbol y Consultas")
        self.root.geometry("1200x800")

        # Inicializar gestores
        self.gestor_datos = GestorDatos()
        self.gestor_familias = GestorFamilias()
        self.datos = {}  # Relaciones inferidas
        self.personas_lista = []  # Lista de (cedula, nombre)
        self.cedula_seleccionada = None

        self.cargar_datos()
        self.crear_widgets()

    def cargar_datos(self):
        """Carga los datos de relaciones.json"""
        try:
            self.datos = self.gestor_datos.cargar_relaciones()
            self.personas_lista = [
                (cedula, datos["nombre"])
                for cedula, datos in self.datos.items()
            ]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
            self.root.quit()

    def refrescar_datos(self):
        """Refresca los datos después de registrar nuevas relaciones"""
        self.cargar_datos()
        # Actualizar las listas en todas las pestañas que las usan
        if hasattr(self, 'tab_familias') and hasattr(self.tab_familias, 'tab_relaciones'):
            self.tab_familias.tab_relaciones.actualizar_lista_personas()

    def crear_widgets(self):
        """Crea los widgets principales: Notebook con pestañas"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # ================== Crear Pestañas ==================
        self.tab_arbol = TabArbol(notebook, self)
        self.tab_consultas = TabConsultas(notebook, self)
        self.tab_familias = TabFamilias(notebook, self)
        self.tab_simulador = TabSimulador(notebook, self)  # ✅ Pestaña nueva

        # ================== Añadir Pestañas al Notebook ==================
        notebook.add(self.tab_arbol.frame, text="Árbol Familiar")
        notebook.add(self.tab_consultas.frame, text="Consultas Avanzadas")
        notebook.add(self.tab_familias.frame, text="Gestión de Familias")
        notebook.add(self.tab_simulador.frame, text="Simulador de Familia")  # ✅ Nueva pestaña visible

        # Barra de estado opcional (opcional)
        self.status_var = tk.StringVar()
        self.status_var.set("Listo.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")


# ================== Ejecución Principal ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFamiliar(root)
    root.mainloop()