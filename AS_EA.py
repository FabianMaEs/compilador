import tkinter as tk
from tkinter import ttk

class TreeViewExample(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TreeView Example")
        self.geometry("400x400")

        self.semantic_tab = ttk.Frame(self)
        self.semantic_tab.pack(fill="both", expand=True)

        # Crear un Treeview
        self.tree = ttk.Treeview(self.semantic_tab)
        self.tree.pack(fill="both", expand=True)

        # Agregar una barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.semantic_tab, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Cargar el árbol
        self.load_tree()

    def load_tree(self):
        # Datos del árbol (puedes reemplazar esto con la lectura del archivo)
        data = """
program
>list-decl
>>decl
>>>tipo (float)
>>>list-id
>>>>a (float: 0.0)
>>>>x (float: 0.0)
>>>>c (float: 0.0)
>>decl
>>>tipo (int)
>>>list-id
>>>>c (float: 0.0)
>>decl
>>>tipo (bool)
>>>list-id
>>>>d (bool: False)
>list-sent
>>sent-assign
>>>a (float: 60.33333333333333)
>>>expr (-: 60.33333333333333)
>>>>expr (+: 61.33333333333333)
>>>>>expr (-: 27.333333333333332)
>>>>>>expr (+: 28)
>>>>>>>factor (int: 24)
>>>>>>>factor (int: 4)
>>>>>>term (*: 0.6666666666666666)
>>>>>>>term (/: 0.3333333333333333)
>>>>>>>>factor (int: 1)
>>>>>>>>factor (int: 3)
>>>>>>>factor (int: 2)
>>>>>factor (int: 34)
>>>>factor (int: 1)
>>sent-assign
>>>x (float: 8.0)
>>>term (*: 8.0)
>>>>expr (-: 2)
>>>>>factor (int: 5)
>>>>>factor (int: 3)
>>>>term (/: 4.0)
>>>>>factor (int: 8)
>>>>>factor (int: 2)
        """
        
        # Procesar los datos y agregar al Treeview
        self.add_tree_nodes(data.strip().splitlines())

    def add_tree_nodes(self, lines):
        # Crear un diccionario para almacenar los nodos y su ID
        node_ids = {}

        for line in lines:
            level = line.count('>')
            node_name = line.strip().replace('>', '').strip()
            # Agregar el nodo a la Treeview
            if level == 0:
                node_id = self.tree.insert("", "end", text=node_name)
            else:
                parent_id = node_ids[level - 1]
                node_id = self.tree.insert(parent_id, "end", text=node_name)
            node_ids[level] = node_id

if __name__ == "__main__":
    app = TreeViewExample()
    app.mainloop()
