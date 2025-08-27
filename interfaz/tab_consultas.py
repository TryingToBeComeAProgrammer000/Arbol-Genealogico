# interfaz/tab_consultas.py
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from buscador.buscador import BuscadorFamiliar
    BUSCADOR_DISPONIBLE = True
except ImportError:
    BUSCADOR_DISPONIBLE = False
    print("Advertencia: No se pudo cargar BuscadorFamiliar")

class TabConsultas:
    def __init__(self, parent, interfaz_principal):
        self.parent = parent
        self.interfaz = interfaz_principal
        self.frame = ttk.Frame(parent)
        self.buscador = None
        self.widgets_consultas = {}
        
        if BUSCADOR_DISPONIBLE:
            try:
                self.buscador = BuscadorFamiliar()
            except Exception as e:
                messagebox.showwarning("Advertencia", f"No se cargó el buscador: {e}")
        
        self.crear_widgets()

    def crear_widgets(self):
        if not self.buscador:
            lbl = ttk.Label(self.frame, text="No se pudo cargar el sistema de consultas.\nVerifica 'buscador.py' y los archivos JSON.", foreground="red", justify="center", font=("Helvetica", 10))
            lbl.pack(pady=50)
            return

        # Canvas con scroll
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Título
        ttk.Label(scrollable_frame, text="🔍 Consultas Familiares Avanzadas", font=("Helvetica", 14, "bold")).pack(pady=15)

        # === Consulta 1: Relación entre A y B ===
        f1 = ttk.LabelFrame(scrollable_frame, text="1. Relación entre dos personas")
        f1.pack(fill="x", padx=10, pady=5)
        ttk.Label(f1, text="Cédula A:").grid(row=0, column=0, padx=5, pady=3)
        ced1 = ttk.Entry(f1, width=15)
        ced1.grid(row=0, column=1, padx=5, pady=3)
        ttk.Label(f1, text="Cédula B:").grid(row=0, column=2, padx=5, pady=3)
        ced2 = ttk.Entry(f1, width=15)
        ced2.grid(row=0, column=3, padx=5, pady=3)
        ttk.Button(f1, text="Consultar", command=lambda: self._consulta1(ced1, ced2)).grid(row=0, column=4, padx=10, pady=3)

        # Resultado 1
        res1 = tk.Text(f1, height=2, width=60, wrap="word")
        res1.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        # === Consulta 2: Primos de X ===
        f2 = ttk.LabelFrame(scrollable_frame, text="2. Primos de primer grado de X")
        f2.pack(fill="x", padx=10, pady=5)
        ttk.Label(f2, text="Cédula:").grid(row=0, column=0, padx=5, pady=3)
        ced_p = ttk.Entry(f2, width=15)
        ced_p.grid(row=0, column=1, padx=5, pady=3)
        ttk.Button(f2, text="Consultar", command=lambda: self._consulta2(ced_p)).grid(row=0, column=2, padx=10, pady=3)
        res2 = tk.Text(f2, height=4, width=60, wrap="word")
        res2.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # === Consulta 3: Antepasados maternos ===
        f3 = ttk.LabelFrame(scrollable_frame, text="3. Antepasados maternos de X")
        f3.pack(fill="x", padx=10, pady=5)
        ttk.Label(f3, text="Cédula:").grid(row=0, column=0, padx=5, pady=3)
        ced_m = ttk.Entry(f3, width=15)
        ced_m.grid(row=0, column=1, padx=5, pady=3)
        ttk.Button(f3, text="Consultar", command=lambda: self._consulta3(ced_m)).grid(row=0, column=2, padx=10, pady=3)
        res3 = tk.Text(f3, height=4, width=60, wrap="word")
        res3.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # === Consulta 4: Descendientes vivos ===
        f4 = ttk.LabelFrame(scrollable_frame, text="4. Descendientes vivos de X")
        f4.pack(fill="x", padx=10, pady=5)
        ttk.Label(f4, text="Cédula:").grid(row=0, column=0, padx=5, pady=3)
        ced_d = ttk.Entry(f4, width=15)
        ced_d.grid(row=0, column=1, padx=5, pady=3)
        ttk.Button(f4, text="Consultar", command=lambda: self._consulta4(ced_d)).grid(row=0, column=2, padx=10, pady=3)
        res4 = tk.Text(f4, height=4, width=60, wrap="word")
        res4.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # === Consulta 5: Nacidos en últimos 10 años ===
        f5 = ttk.LabelFrame(scrollable_frame, text="5. Personas nacidas en últimos 10 años")
        f5.pack(fill="x", padx=10, pady=5)
        ttk.Button(f5, text="Consultar", command=lambda: self._consulta5()).pack(pady=5)
        res5 = tk.Text(f5, height=6, width=60, wrap="word")
        res5.pack(padx=5, pady=5)

        # === Consulta 6: Parejas con 2+ hijos en común ===
        f6 = ttk.LabelFrame(scrollable_frame, text="6. Parejas con 2 o más hijos en común")
        f6.pack(fill="x", padx=10, pady=5)
        ttk.Button(f6, text="Consultar", command=lambda: self._consulta6()).pack(pady=5)
        res6 = tk.Text(f6, height=8, width=60, wrap="word")
        res6.pack(padx=5, pady=5)

        # === Consulta 7: Fallecidos antes de 50 ===
        f7 = ttk.LabelFrame(scrollable_frame, text="7. Personas fallecidas antes de 50 años")
        f7.pack(fill="x", padx=10, pady=5)
        ttk.Button(f7, text="Consultar", command=lambda: self._consulta7()).pack(pady=5)
        res7 = tk.Text(f7, height=6, width=60, wrap="word")
        res7.pack(padx=5, pady=5)

        # Guardar referencias
        self.widgets_consultas = {
            '1': {'ced1': ced1, 'ced2': ced2, 'res': res1},
            '2': {'ced': ced_p, 'res': res2},
            '3': {'ced': ced_m, 'res': res3},
            '4': {'ced': ced_d, 'res': res4},
            '5': {'res': res5},
            '6': {'res': res6},
            '7': {'res': res7}
        }

    # === Funciones de consulta ===
    def _consulta1(self, entry_a, entry_b):
        a, b = entry_a.get().strip(), entry_b.get().strip()
        if not a or not b:
            messagebox.showwarning("Advertencia", "Ingrese ambas cédulas.")
            return
        try:
            res = self.buscador.relacion_entre(a, b)
            self._mostrar_y_limpiar(self.widgets_consultas['1']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['1']['res'], f"Error: {e}")

    def _consulta2(self, entry):
        ced = entry.get().strip()
        if not ced:
            messagebox.showwarning("Advertencia", "Ingrese una cédula.")
            return
        try:
            primos = self.buscador.primos_de(ced)
            res = "\n".join([f"• {nombre} (Cédula: {c})" for c, nombre in primos]) or "Ninguno"
            self._mostrar_y_limpiar(self.widgets_consultas['2']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['2']['res'], f"Error: {e}")

    def _consulta3(self, entry):
        ced = entry.get().strip()
        if not ced:
            messagebox.showwarning("Advertencia", "Ingrese una cédula.")
            return
        try:
            ancestros = self.buscador.antepasados_maternos(ced)
            res = "\n".join([f"• {nombre} (Cédula: {c})" for c, nombre in ancestros]) or "Ninguno"
            self._mostrar_y_limpiar(self.widgets_consultas['3']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['3']['res'], f"Error: {e}")

    def _consulta4(self, entry):
        ced = entry.get().strip()
        if not ced:
            messagebox.showwarning("Advertencia", "Ingrese una cédula.")
            return
        try:
            vivos = self.buscador.descendientes_vivos(ced)
            res = "\n".join([f"• {nombre} (Cédula: {c})" for c, nombre in vivos]) or "Ninguno"
            self._mostrar_y_limpiar(self.widgets_consultas['4']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['4']['res'], f"Error: {e}")

    def _consulta5(self):
        try:
            nacidos = self.buscador.nacidos_ultimos_10_anios()
            res = f"Total: {len(nacidos)} personas\n\n"
            res += "\n".join([f"• {n[1]} (Nacido: {n[2]})" for n in nacidos])
            self._mostrar_y_limpiar(self.widgets_consultas['5']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['5']['res'], f"Error: {e}")

    def _consulta6(self):
        try:
            parejas = self.buscador.parejas_con_2_o_mas_hijos()
            if not parejas:
                res = "Ninguna pareja con 2+ hijos en común."
            else:
                res = ""
                for p in parejas:
                    res += f"• {p['pareja']} → {p['hijos_comunes']} hijos\n"
                    res += "  Hijos: " + ", ".join(p['nombres_hijos']) + "\n\n"
            self._mostrar_y_limpiar(self.widgets_consultas['6']['res'], res.strip())
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['6']['res'], f"Error: {e}")

    def _consulta7(self):
        try:
            total, detalles = self.buscador.fallecidos_menos_50()
            res = f"Total: {total} personas\n\n"
            res += "\n".join([f"• {d['nombre']} - {d['edad']} años (Fallecido: {d['fallecimiento']})" for d in detalles])
            self._mostrar_y_limpiar(self.widgets_consultas['7']['res'], res)
        except Exception as e:
            self._mostrar_y_limpiar(self.widgets_consultas['7']['res'], f"Error: {e}")

    def _mostrar_y_limpiar(self, text_widget, texto):
        text_widget.config(state="normal")
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, texto)
        text_widget.config(state="disabled")