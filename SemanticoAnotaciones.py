class Node:
    def __init__(self, nombre, tipo=None, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def add_hijo(self, hijo):
        self.hijos.append(hijo)

    def __str__(self):
        return f"{self.nombre} ({self.tipo}: {self.valor})"

class ExprNode(Node):
    def __init__(self, operacion, tipo=None, valor=None):
        super().__init__(nombre="expr", tipo=tipo, valor=valor)
        self.operacion = operacion

    def __str__(self):
        return f"expr ({self.operacion}: {self.valor})"

class TermNode(Node):
    def __init__(self, operacion, tipo=None, valor=None):
        super().__init__(nombre="term", tipo=tipo, valor=valor)
        self.operacion = operacion

    def __str__(self):
        return f"term ({self.operacion}: {self.valor})"
    
class AssignNode(Node):
    def __init__(self, operacion = '=', tipo=None, valor=None):
        super().__init__(nombre="sent-assign", tipo=tipo, valor=valor)
        self.operacion = operacion

    def __str__(self):
        return f"sent-assign ({self.operacion}: {self.valor})"

def parse_ast(lines):
    stack = []
    root = None

    for line in lines:
        indent_level = line.count('>')  # Cuenta el número de '>' para la indentación
        content = line.strip('>').strip()  # Elimina '>' y espacios en blanco

        # Crear el nodo correspondiente
        if content.startswith("id"):
            nombre = content.split(" ")[1].strip("()")
            node = Node(nombre=nombre, tipo="id", valor=-11)
        elif content.startswith("factor"):
            valor = content.split(" ")[1].strip("()")
            valor = float(valor)
            if valor.is_integer():
                valor = int(valor)
            node = Node(nombre="factor", tipo="factor", valor=valor)
        elif content.startswith("expr"):
            operacion = content.split(" ")[1].strip("()") if len(content.split(" ")) > 1 else None
            node = ExprNode(operacion=operacion)
        elif content.startswith("term"):
            operacion = content.split(" ")[1].strip("()") if len(content.split(" ")) > 1 else None
            node = TermNode(operacion=operacion)
        elif content.startswith("sent-assign"):
            node = AssignNode(operacion="=")
            print("AssignNode:", node)
        else:
            node = Node(nombre=content)

        if indent_level == 0:
            root = node
        else:
            while len(stack) > indent_level:
                stack.pop()
            stack[-1].add_hijo(node)

        stack.append(node)

    return root

def extract_variables():
    variables = {}
    with open('salidas/tabla_simbolos.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            nombre = parts[0]
            tipo = parts[1]
            valor = parts[3]
            if tipo == "int":
                valor = int(valor)
            elif tipo == "float":
                valor = float(valor)
            elif tipo == "bool":
                valor = valor.lower() == "true"
            variables[nombre] = (tipo, valor)

    return variables

def evaluate(node, variables):
    if isinstance(node, ExprNode) or isinstance(node, TermNode) or isinstance(node, AssignNode):
        left = evaluate(node.hijos[0], variables)
        right = evaluate(node.hijos[1], variables)
        if node.operacion == "+":
            node.valor = left + right
        elif node.operacion == "-":
            node.valor = left - right
        elif node.operacion == "*":
            node.valor = left * right
        elif node.operacion == "/":
            if right == 0:
                with open('salidas/errors.txt', 'a') as file:
                    file.write("Error: División por cero no permitida\n")
                raise ValueError("Division by zero is not allowed")
            node.valor = left / right
        elif node.operacion == "=":
            print(f"Assigning {node.hijos[0].nombre} to {right}")
            node.hijos[0].valor = right
            if node.hijos[0].nombre in variables:
                # Actualizar el valor de la variable en variables
                tipo = variables[node.hijos[0].nombre][0]
                variables[node.hijos[0].nombre] = (tipo, right)
                if node.hijos[0].tipo == "int" and isinstance(right, float):
                    with open('salidas/errors.txt', 'a') as file:
                        file.write(f"Error: {node.hijos[0].nombre} debe ser un entero, pero es float.\n")
                    print(f"Error: {node.hijos[0].nombre} debe ser un entero, pero es float.")
                elif node.hijos[0].tipo == "float":
                    node.hijos[0].valor = float(right)
        node.tipo = type(node.valor).__name__
        return node.valor
    return node.valor

def annotate_tree(node, variables, no_declared):
    # Primero recorremos los hijos
    for hijo in node.hijos:
        annotate_tree(hijo, variables, no_declared)

    # Luego evaluamos o anotamos el nodo actual
    if isinstance(node, ExprNode) or isinstance(node, TermNode) or isinstance(node, AssignNode):
        evaluate(node, variables)  # Evalúa y actualiza el nodo

    elif node.tipo == "factor":
        node.tipo = type(node.valor).__name__
    elif node.tipo == "id":
        # Asignar el valor de la variable
        if node.nombre in no_declared:
            node.tipo = "Error"
            node.valor = "No declarada"
        else:
            if node.nombre in variables:
                variable_tipo, variable_valor = variables[node.nombre]
                node.tipo = variable_tipo
                node.valor = variable_valor
                # Verificar el tipo de la variable y validar
                if variable_tipo == "int" and isinstance(node.valor, float):
                    with open('salidas/errors.txt', 'a') as file:
                        file.write(f"Error: {node.nombre} debe ser un entero, pero es float.\n")
                elif variable_tipo == "float":
                    node.valor = float(node.valor)  # Asegúrate de que el valor sea un float
                    #print(f"Variable '{node.nombre}' asignada con valor: {node.valor}")
                elif variable_tipo == "bool" and not isinstance(node.valor, bool):
                    print(f"Error: {node.nombre} debe ser un booleano.")
            else:
                node.tipo = "Error"
                node.valor = "No declarada"

def print_tree(node, variables, indent=0):
    indent_str = ">" * indent
    
    if isinstance(node, ExprNode) or isinstance(node, TermNode):
        print(f"{indent_str}{node.nombre} ({node.operacion}: {node.valor})")
    elif node.nombre in ("program", "list-decl", "list-sent", "sent-assign","decl", "list-id") or node.nombre.startswith("tipo"):
        print(f"{indent_str}{node.nombre}")
    elif node.tipo == "id":
        # Imprimir el tipo de la variable de la tabla de símbolos si está definida
        if node.nombre in variables:
            tipo = variables[node.nombre]
            print(f"{indent_str}{node.nombre} ({tipo}: {node.valor}) aaaaaaaa" )
            if(tipo == "int" and not node.valor.is_integer()):
                error = (f"{indent_str}Error: {node.nombre} no es un entero")
            elif(tipo == "float" and node.valor.is_integer()):
                error = (f"{indent_str}Error: {node.nombre} no es un flotante")
            elif(tipo == "bool" and not isinstance(node.valor, bool)):
                error = (f"{indent_str}Error: {node.nombre} no es un booleano")
            with open('salidas/errors.txt', 'a') as file:
                file.write(error + "\n")
        else:
            print(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})nnnnnnnnnn")
    else:
        print(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})")
    for hijo in node.hijos:
        print_tree(hijo, variables, indent + 1)
        
def save_tree(root, variables, ruta):
    def write_node(node, file, indent=0):
        indent_str = ">" * indent
        if isinstance(node, ExprNode) or isinstance(node, TermNode):
            file.write(f"{indent_str}{node.nombre} ({node.operacion}: {node.valor})\n")
        elif node.nombre in ("program", "list-decl", "list-sent", "sent-assign", "decl", "list-id") or node.nombre.startswith("tipo"):
            file.write(f"{indent_str}{node.nombre}\n")
        elif node.tipo == "id":
            if node.nombre in variables:
                tipo = variables[node.nombre]
                file.write(f"{indent_str}{node.nombre} ({tipo}: {node.valor})\n")
                # Actualizar el valor si en la tabla de símbolos (posicion 3) es diferente al valor actual
                if node.valor != variables[node.nombre][1]:
                    variables[node.nombre] = (tipo, node.valor)
                with open('salidas/errors.txt', 'a') as error_file:
                    if(tipo == "int" and not node.valor.is_integer()):
                        error = (f"{indent_str}Error: {node.nombre} no es un entero")
                    elif(tipo == "float" and node.valor.is_integer()):
                        error = (f"{indent_str}Error: {node.nombre} no es un flotante")
                    elif(tipo == "bool" and not isinstance(node.valor, bool)):
                        error = (f"{indent_str}Error: {node.nombre} no es un booleano")
                    error_file.write(error + "\n")
            else:
                file.write(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})\n")
        else:
            file.write(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})\n")
        for hijo in node.hijos:
            write_node(hijo, file, indent + 1)

    with open(ruta, "w") as file:
        write_node(root, file)

def update_variable_in_file(nombre, nuevo_valor):
    # Lee las líneas del archivo
    with open('salidas/tabla_simbolos.txt', 'r') as file:
        lines = file.readlines()

    # Crea una lista para almacenar las líneas actualizadas
    updated_lines = []

    # Itera sobre cada línea y actualiza el valor si corresponde
    for line in lines:
        parts = line.split()
        if len(parts) >= 4 and parts[0] == nombre:  # Verifica si es la variable a actualizar
            parts[3] = str(nuevo_valor)  # Actualiza el valor en la tercera posición
            updated_line = ' '.join(parts)  # Une de nuevo las partes en una línea
            updated_lines.append(updated_line + '\n')  # Agrega la línea actualizada
        else:
            updated_lines.append(line)  # Agrega la línea original si no se actualiza

    # Escribe las líneas actualizadas de nuevo en el archivo
    with open('salidas/tabla_simbolos.txt', 'w') as file:
        file.writelines(updated_lines)


# Leer el archivo AST.TXT
with open('salidas/ast.txt', 'r') as file:
    lines = file.readlines()

# Parsear el árbol AST
root = parse_ast(lines)

# Extraer variables
variables = extract_variables()
print("Variables:", variables)
no_declared = []
with open('salidas/errors.txt', 'r') as file:
    for line in file:
        if(line.startswith("Variable no declarada")):
            var = line.split("'")[1]
            no_declared.append(var)

# Anotar el árbol
annotate_tree(root, variables, no_declared)


# Mostrar el árbol anotado
print_tree(root, variables)
save_tree(root, variables, "salidas/ast_anotado.txt")

print("Variables actualizadas:", variables)

# Actualizar el valor de las variables en el archivo de la tabla de símbolos
with open('salidas/tabla_simbolos.txt', 'r') as file:
    lines = file.readlines()
for line in lines:
    parts = line.split()
    if len(parts) >= 4:
        nombre = parts[0]
        valor = variables[nombre][1]
        print(f"Variable '{nombre}' tiene valor: {valor}")
        update_variable_in_file(nombre, valor)