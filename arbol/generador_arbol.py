# arbol/generador_arbol.py
import networkx as nx
import matplotlib.pyplot as plt

class GeneradorArbol:
    def __init__(self):
        pass

    def crear_arbol_familiar(self, cedula_principal, datos, nombre_principal):
        """Genera el árbol familiar para una persona"""
        G = nx.Graph()
        visited = set()
        MAX_NIVEL = 3

        def agregar(ced, nivel=0, relacion=""):
            if ced in visited or nivel > MAX_NIVEL or ced not in datos:
                return
            visited.add(ced)
            nombre = datos[ced]["nombre"][:18] + "..." if len(datos[ced]["nombre"]) > 18 else datos[ced]["nombre"]
            G.add_node(ced, label=f"{nombre}\n({relacion})")

            if nivel < MAX_NIVEL:
                rels = datos[ced]["relaciones"]
                for p in rels["padres"]:
                    if p in datos:
                        G.add_edge(ced, p)
                        agregar(p, nivel + 1, "Padre/Madre")
                for h in rels["hijos"]:
                    if h in datos:
                        G.add_edge(ced, h)
                        agregar(h, nivel + 1, "Hijo(a)")
                pareja = rels["pareja"]
                if pareja and pareja in datos:
                    G.add_edge(ced, pareja)
                    agregar(pareja, nivel, "Pareja")
                if nivel == 0:
                    for hermano in rels["hermanos"][:3]:
                        if hermano in datos:
                            G.add_edge(ced, hermano)
                            agregar(hermano, nivel + 1, "Hermano(a)")

        agregar(cedula_principal, 0, "Principal")

        if len(G.nodes()) == 0:
            return None

        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2.5, iterations=50)
        labels = nx.get_node_attributes(G, 'label')
        node_colors = ['lightblue'] * len(G.nodes())
        nx.draw(G, pos, with_labels=True, labels=labels, node_color=node_colors,
                node_size=1800, font_size=9, edge_color='gray', font_weight='bold', ax=ax)
        ax.set_title(f"Árbol Familiar: {nombre_principal}", fontsize=14)
        ax.axis('off')
        plt.tight_layout()
        
        return fig