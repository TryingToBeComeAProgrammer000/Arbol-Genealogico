# main.py
import tkinter as tk
from interfaz.interfaz_principal import InterfazFamiliar

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFamiliar(root)
    root.mainloop()