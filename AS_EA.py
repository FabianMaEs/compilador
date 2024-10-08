import tkinter as tk
from tkinter import ttk

# Definimos una clase para los nodos del árbol
class NodoAST:
    def __init__(self, valor, tipo=None):
        self.valor = valor      # El valor puede ser un número, variable o un operador
        self.tipo = tipo        # Puede ser 'int', 'float', etc.
        self.hijos = []         # Lista de hijos del nodo (si es un operador tendrá operandos)

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

# Función para evaluar el árbol y anotar los valores intermedios
def evaluar_arbol(nodo):
    if len(nodo.hijos) == 0:
        # Si es una hoja (un número o variable), solo devolvemos su valor
        return float(nodo.valor)

    # Evaluamos los hijos (operandos)
    operando_izq = evaluar_arbol(nodo.hijos[0])
    operando_der = evaluar_arbol(nodo.hijos[1])

    # Dependiendo del operador, evaluamos la operación
    if nodo.valor == '+':
        resultado = operando_izq + operando_der
    elif nodo.valor == '-':
        resultado = operando_izq - operando_der
    elif nodo.valor == '*':
        resultado = operando_izq * operando_der
    elif nodo.valor == '/':
        resultado = operando_izq / operando_der
    elif nodo.valor == '%':
        resultado = operando_izq % operando_der
    elif nodo.valor == '^':
        resultado = operando_izq ** operando_der

    # Anotamos el valor resultante en el nodo
    nodo.tipo = 'float' if isinstance(resultado, float) else 'int'
    nodo.valor = resultado
    return resultado

# Función para crear un árbol de ejemplo (AST)
def crear_ast():
    # Construimos el árbol sintáctico de la expresión: (3 + 5) * 2
    nodo_mas = NodoAST('+')
    nodo_mas.agregar_hijo(NodoAST('3'))
    nodo_mas.agregar_hijo(NodoAST('5'))

    nodo_mult = NodoAST('*')
    nodo_mult.agregar_hijo(nodo_mas)
    nodo_mult.agregar_hijo(NodoAST('2'))

    return nodo_mult

# Función recursiva para construir el árbol en la interfaz
def mostrar_arbol(nodo, padre, tree):
    nodo_id = tree.insert(padre, 'end', text=f'{nodo.valor} [{nodo.tipo}]')
    for hijo in nodo.hijos:
        mostrar_arbol(hijo, nodo_id, tree)

# Configuración de la interfaz gráfica con tkinter
def mostrar_arbol_interactivo(arbol):
    root = tk.Tk()
    root.title("Árbol con Anotaciones - Expansión y Colapsado")
    root.geometry("400x400")

    # Definir un árbol de interfaz (tkinter Treeview)
    tree = ttk.Treeview(root)
    tree.pack(fill=tk.BOTH, expand=True)

    # Llamamos a la función recursiva para mostrar el árbol
    mostrar_arbol(arbol, '', tree)

    # Botón para salir
    boton_salir = tk.Button(root, text="Cerrar", command=root.quit)
    boton_salir.pack(pady=10)

    root.mainloop()

# Crear el AST y evaluarlo
arbol = crear_ast()
evaluar_arbol(arbol)

# Mostrar el árbol en la interfaz
mostrar_arbol_interactivo(arbol)
