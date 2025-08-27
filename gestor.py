# gestor.py
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class GestorFamiliar:
    def __init__(self, personas_file="personas.json", matrimonios_file="matrimonios.json"):
        self.personas_file = personas_file
        self.matrimonios_file = matrimonios_file
        self.personas = self.cargar_personas()
        self.matrimonios = self.cargar_matrimonios()
        self.apellidos_existentes = self.extraer_apellidos()

    def cargar_personas(self):
        try:
            with open(self.personas_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("personas.json debe contener una lista")
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            raise ValueError(f"Error en formato JSON de personas.json: {e}")

    def cargar_matrimonios(self):
        try:
            with open(self.matrimonios_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("matrimonios.json debe contener una lista")
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            raise ValueError(f"Error en formato JSON de matrimonios.json: {e}")

    def extraer_apellidos(self):
        """Extrae todos los apellidos únicos de las personas cargadas."""
        apellidos = set()
        for p in self.personas:
            a1 = str(p.get("apellido1", "")).strip().lower()
            a2 = str(p.get("apellido2", "")).strip().lower()
            if a1:
                apellidos.add(a1.title())
            if a2:
                apellidos.add(a2.title())
        return sorted(apellidos)

    def calcular_edad(self, fecha_nacimiento):
        """Calcula la edad a partir de la fecha de nacimiento (YYYY-MM-DD)."""
        if not fecha_nacimiento or not isinstance(fecha_nacimiento, str):
            return None
        try:
            nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
            hoy = datetime.now()
            edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
            return edad if edad >= 0 else None
        except ValueError:
            return None

    def agregar_persona(self, nombre, apellido1, apellido2=None):
        """Agrega una nueva persona con nombre y apellidos (solo si no existe cédula duplicada)."""
        # Generar cédula temporal (puedes cambiarlo por entrada manual si quieres)
        max_cedula = max([int(p["cedula"]) for p in self.personas if str(p["cedula"]).isdigit()] + [10000000])
        nueva_cedula = str(max_cedula + 1)

        nueva_persona = {
            "cedula": nueva_cedula,
            "nombre": nombre.strip().title(),
            "apellido1": apellido1.strip().title(),
            "apellido2": apellido2.strip().title() if apellido2 else "",
            "fecha_nacimiento": "",  # Se puede extender para pedir fecha
        }

        self.personas.append(nueva_persona)
        self.apellidos_existentes = self.extraer_apellidos()  # Actualizar
        messagebox.showinfo("Éxito", f"Persona agregada: {nombre} (Cédula: {nueva_cedula})")
        return nueva_cedula

    def agregar_matrimonio(self, cedula1, cedula2):
        """Agrega un matrimonio si cumple con las condiciones de edad."""
        p1 = next((p for p in self.personas if p["cedula"] == cedula1), None)
        p2 = next((p for p in self.personas if p["cedula"] == cedula2), None)

        if not p1 or not p2:
            raise ValueError("Una de las cédulas no existe.")

        edad1 = self.calcular_edad(p1.get("fecha_nacimiento"))
        edad2 = self.calcular_edad(p2.get("fecha_nacimiento"))

        if edad1 is None or edad2 is None:
            raise ValueError("Falta fecha de nacimiento para verificar edad.")

        if edad1 < 18:
            raise ValueError(f"{p1['nombre']} tiene {edad1} años. Debe tener al menos 18.")
        if edad2 < 18:
            raise ValueError(f"{p2['nombre']} tiene {edad2} años. Debe tener al menos 18.")

        if abs(edad1 - edad2) > 15:
            raise ValueError(f"Diferencia de edad ({abs(edad1 - edad2)}) supera los 15 años permitidos.")

        # Evitar duplicados
        ya_casados = any(
            (m.get("conyuge1_cedula") == cedula1 and m.get("conyuge2_cedula") == cedula2) or
            (m.get("conyuge1_cedula") == cedula2 and m.get("conyuge2_cedula") == cedula1)
            for m in self.matrimonios
        )
        if ya_casados:
            raise ValueError("Este matrimonio ya está registrado.")

        nuevo_mat = {
            "conyuge1_cedula": cedula1,
            "conyuge2_cedula": cedula2,
            "fecha_matrimonio": datetime.now().strftime("%Y-%m-%d")
        }
        self.matrimonios.append(nuevo_mat)
        messagebox.showinfo("Éxito", f"Matrimonio registrado entre {p1['nombre']} y {p2['nombre']}.")

    def guardar_datos(self):
        """Guarda los cambios en los archivos JSON."""
        try:
            with open(self.personas_file, "w", encoding="utf-8") as f:
                json.dump(self.personas, f, ensure_ascii=False, indent=2)
            with open(self.matrimonios_file, "w", encoding="utf-8") as f:
                json.dump(self.matrimonios, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardado", "Datos guardados correctamente en archivos JSON.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {e}")


# --- Interfaz para el gestor ---
class InterfazGestor:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor Familiar - Agregar Personas y Matrimonios")
        self.root.geometry("700x600")

        self.gestor = GestorFamiliar()

        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Sección: Agregar Persona ---
        persona_frame = ttk.LabelFrame(main_frame, text="Agregar Nueva Persona", padding="10")
        persona_frame.pack(fill="x", pady=10)

        ttk.Label(persona_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nombre_entry = ttk.Entry(persona_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(persona_frame, text="Apellido 1:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.apellido1_combo = ttk.Combobox(persona_frame, state="readonly", width=27)
        self.apellido1_combo.grid(row=1, column=1, padx=5, pady=5)
        self.apellido1_combo['values'] = self.gestor.apellidos_existentes

        ttk.Label(persona_frame, text="Apellido 2 (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.apellido2_combo = ttk.Combobox(persona_frame, state="readonly", width=27)
        self.apellido2_combo.grid(row=2, column=1, padx=5, pady=5)
        self.apellido2_combo['values'] = [""] + self.gestor.apellidos_existentes
        self.apellido2_combo.current(0)

        ttk.Button(persona_frame, text="Agregar Persona", command=self.agregar_persona).grid(
            row=3, column=0, columnspan=2, pady=10)

        # --- Sección: Agregar Matrimonio ---
        matrimonio_frame = ttk.LabelFrame(main_frame, text="Registrar Matrimonio", padding="10")
        matrimonio_frame.pack(fill="x", pady=10)

        ttk.Label(matrimonio_frame, text="Cónyuge 1 (Cédula):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cedula1_entry = ttk.Entry(matrimonio_frame, width=20)
        self.cedula1_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(matrimonio_frame, text="Cónyuge 2 (Cédula):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cedula2_entry = ttk.Entry(matrimonio_frame, width=20)
        self.cedula2_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(matrimonio_frame, text="Registrar Matrimonio", command=self.registrar_matrimonio).grid(
            row=2, column=0, columnspan=2, pady=10)

        # --- Botón Guardar ---
        ttk.Button(main_frame, text="Guardar Todos los Cambios", command=self.guardar).pack(pady=20)

    def agregar_persona(self):
        nombre = self.nombre_entry.get().strip()
        apellido1 = self.apellido1_combo.get().strip()
        apellido2 = self.apellido2_combo.get().strip()

        if not nombre or not apellido1:
            messagebox.showwarning("Advertencia", "Nombre y primer apellido son obligatorios.")
            return

        try:
            self.gestor.agregar_persona(nombre, apellido1, apellido2)
            # Actualizar combos por si se agregan más personas
            self.nombre_entry.delete(0, tk.END)
            self.apellido1_combo.set("")
            self.apellido2_combo.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def registrar_matrimonio(self):
        cedula1 = self.cedula1_entry.get().strip()
        cedula2 = self.cedula2_entry.get().strip()

        if not cedula1 or not cedula2:
            messagebox.showwarning("Advertencia", "Ambas cédulas son obligatorias.")
            return

        if cedula1 == cedula2:
            messagebox.showwarning("Advertencia", "Una persona no puede casarse consigo misma.")
            return

        try:
            self.gestor.agregar_matrimonio(cedula1, cedula2)
            self.cedula1_entry.delete(0, tk.END)
            self.cedula2_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def guardar(self):
        self.gestor.guardar_datos()


# --- Ejecutar solo esta interfaz ---
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGestor(root)
    root.mainloop()