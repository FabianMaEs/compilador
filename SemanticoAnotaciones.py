import subprocess
import sys


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
        indent_level = line.count('?')  # Cuenta el número de '?' para la indentación
        content = line.strip('?').strip()  # Elimina '?' y espacios en blanco

        # Crear el nodo correspondiente
        if content.startswith("id"):
            nombre = content.split(" ")[1].strip("()")
            node = Node(nombre=nombre, tipo="id", valor=-11)
        elif content.startswith("factor"):
            valor = content.split(" ")[1].strip("()")
            try:
                valor = float(valor)
                if valor.is_integer():
                    valor = int(valor)
            except ValueError:
                # Si no es un número, buscar en la tabla de símbolos
                if valor in variables:
                    nombre,
                    valor = variables[valor][1]  # Obtener el valor de la tabla de símbolos
                    node = Node(nombre=nombre, tipo=variables[nombre][0], valor=valor)
                else:
                    raise ValueError(f"Variable '{valor}' no declarada y no es un número.")
            node = Node(nombre=nombre, tipo=variables[nombre][0], valor=valor)
        elif content.startswith("expr"):
            operacion = content.split(" ")[1].strip("()") if len(content.split(" ")) > 1 else None
            node = ExprNode(operacion=operacion)
        elif content.startswith("term"):
            operacion = content.split(" ")[1].strip("()") if len(content.split(" ")) > 1 else None
            node = TermNode(operacion=operacion)
        elif content.startswith("sent-assign"):
            node = AssignNode(operacion="=")
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

### Corregir errores en asignación de variables
def evaluate(node, variables): 
    
    if isinstance(node, ExprNode) or isinstance(node, TermNode):
        
        print(f"Evaluating {node.nombre} ({node.operacion} {node.hijos[0].nombre} {node.hijos[1].nombre})")
        if isinstance(node.hijos[0], Node):
            print(node.hijos[0])
            
        left = evaluate(node.hijos[0], variables)
        right = evaluate(node.hijos[1], variables)
        
        # Realizamos la operación y luego asignamos el valor al nodo
        result = None
        if node.operacion == "+":
            result = left + right
        elif node.operacion == "-":
            result = left - right
        elif node.operacion == "*":
            result = left * right
        elif node.operacion == "/":
            if right == 0:
                with open('salidas/errors.txt', 'a') as file:
                    file.write("Error: División por cero no permitida\n")
                raise ValueError("Division by zero is not allowed")
            result = left / right
        # Asignamos el valor calculado y el tipo
        node.valor = result
        node.tipo = type(node.valor).__name__
        return node.valor

    elif isinstance(node, AssignNode):
        # Evaluamos el lado derecho antes de asignar
        right = evaluate(node.hijos[1], variables)
        left_name = node.hijos[0].nombre
        
        print(f"Assigning {left_name} to {right}")

        # Asignamos el valor al nodo y a las variables
        node.hijos[0].valor = right
        if left_name in variables:
            tipo = variables[left_name][0]
            variables[left_name] = (tipo, right)

            if node.hijos[0].tipo == "int" and isinstance(right, float):
                verificarErrores()
                with open('salidas/errors.txt', 'a') as file:
                    file.write(f"Error: {left_name} debe ser un entero, pero es float.\n")
                print(f"Error: {left_name} debe ser un entero, pero es float.")
            elif node.hijos[0].tipo == "float":
                node.hijos[0].valor = float(right)

        return node.hijos[0].valor

    return node.valor

def verificarErrores():
    with open('salidas/errors.txt', 'r') as error_file:
        lines = error_file.readlines()
        if lines and lines[0].startswith("No errors found"):
            # Eliminar todo el contenido del archivo
            with open('salidas/errors.txt', 'w') as error_file:
                error_file.write("")

def annotate_tree(node, variables, no_declared):
    # Primero recorremos los hijos del nodo
    for hijo in node.hijos:
        annotate_tree(hijo, variables, no_declared)
        

    # Luego evaluamos o anotamos el nodo actual
    if isinstance(node, ExprNode) or isinstance(node, TermNode) or isinstance(node, AssignNode):
        # Evaluamos el nodo primero
        evaluate(node, variables)
        
        # Actualizamos la tabla de símbolos
        with open('salidas/tabla_simbolos.txt', 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                nombre = parts[0]
                valor = variables[nombre][1]

                # print(f"Variable '{nombre}' tiene valor: {valor}")

                # Validaciones de tipos
                if variables[nombre][0] == "int" and isinstance(valor, float):
                    verificarErrores()
                    with open('salidas/errors.txt', 'a') as file:
                        file.write(f"Error: El valor de '{nombre}' debe ser entero, pero es float.\n")
                elif variables[nombre][0] == "float" and isinstance(valor, int):
                    update_variable_in_file(nombre, float(valor), parts[4])
                else:
                    update_variable_in_file(nombre, valor, parts[4])

        # Extraemos las variables actualizadas después de evaluar
        variables = extract_variables()

    elif node.tipo == "factor":
        node.tipo = type(node.valor).__name__

    elif node.tipo == "id":
        if node.nombre in no_declared:
            node.tipo = "Error"
            node.valor = "No declarada"
        else:
            if node.nombre in variables:
                variable_tipo, variable_valor = variables[node.nombre]
                node.tipo = variable_tipo
                node.valor = variable_valor

                # Validaciones de tipos
                if variable_tipo == "int" and isinstance(node.valor, float):
                    verificarErrores()
                    with open('salidas/errors.txt', 'a') as file:
                        file.write(f"Error: {node.nombre} debe ser un entero, pero es float.\n")
                elif variable_tipo == "float":
                    node.valor = float(node.valor)
                elif variable_tipo == "bool" and not isinstance(node.valor, bool):
                    #print(f"Error: {node.nombre} debe ser un booleano.")
                    pass
            else:
                node.tipo = "Error"
                node.valor = "No declarada"


def print_tree(node, variables, indent=0):
    indent_str = "?" * indent
    
    if isinstance(node, ExprNode) or isinstance(node, TermNode):
        print(f"{indent_str}{node.nombre} ({node.operacion}: {node.valor})")
    elif node.nombre in ("program", "list-decl", "list-sent", "sent-assign","decl", "list-id", ) or node.nombre.startswith("tipo"):
        print(f"{indent_str}{node.nombre}")
    elif node.tipo == "id":
        # Imprimir el tipo de la variable de la tabla de símbolos si está definida
        if node.nombre in variables:
            tipo = variables[node.nombre]
            print(f"{indent_str}{node.nombre} ({tipo}: {node.valor})" )
            error = None
            if(tipo == "int" and not node.valor.is_integer()):
                error = (f"{indent_str}Error: {node.nombre} no es un entero")
            elif(tipo == "float" and node.valor.is_integer()):
                error = (f"{indent_str}Error: {node.nombre} no es un flotante")
            elif(tipo == "bool" and not isinstance(node.valor, bool)):
                error = (f"{indent_str}Error: {node.nombre} no es un booleano")
            if error:
                verificarErrores()
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
        indent_str = "?" * indent
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
                    error = None
                    variables[node.nombre] = (tipo, node.valor)
                    if(tipo == "int" and not node.valor.is_integer()):
                        error = (f"{indent_str}Error: {node.nombre} no es un entero")
                    elif(tipo == "float" and node.valor.is_integer()):
                        error = (f"{indent_str}Error: {node.nombre} no es un flotante")
                    elif(tipo == "bool" and not isinstance(node.valor, bool)):
                        error = (f"{indent_str}Error: {node.nombre} no es un booleano")
                    
                if error:
                    verificarErrores()
                    with open('salidas/errors.txt', 'a') as error_file:
                        error_file.write(error + "\n")
                    
            else:
                file.write(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})\n")
        else:
            file.write(f"{indent_str}{node.nombre} ({node.tipo}: {node.valor})\n")
        for hijo in node.hijos:
            write_node(hijo, file, indent + 1)

    with open(ruta, "w") as file:
        write_node(root, file)

def update_variable_in_file(nombre, nuevo_valor, posicion):
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
            # print(f"Actualizando variable '{nombre}' con valor: {nuevo_valor}")
            parts[4] = posicion  # Actualiza la posición
            updated_line = '\t'.join(parts)  # Une de nuevo las partes en una línea
            updated_lines.append(updated_line + '\n')  # Agrega la línea actualizada
        else:
            updated_lines.append(line)  # Agrega la línea original si no se actualiza

    # Escribe las líneas actualizadas de nuevo en el archivo
    with open('salidas/tabla_simbolos.txt', 'w') as file:
        file.writelines(updated_lines)


# Ejecutar TablaSimbolos.py
try:
    print("Ejecutando TablaSimbolos.py...")
    subprocess.run(["python", "TablaSimbolos.py"], check=True)
except subprocess.CalledProcessError as e:
    print("Error al ejecutar TablaSimbolos.py")
    print(e.stderr)
    sys.exit(1)

# Si el archivo errors.txt empieza con "Error", no hace nada
with open('salidas/errors.txt', 'r') as error_file:
    lines_error = error_file.readlines()
    print("Errores:", lines_error)
    if lines_error and lines_error[0].startswith("Error") or lines_error[0].startswith("Variable"):
        print("Error en el archivo de errores")
        sys.exit(1)
    else:
        variables = extract_variables()
        print("Variables:", variables)

        # Leer el archivo AST.TXT
        with open('salidas/ast.txt', 'r') as file:
            lines = file.readlines()
        # Parsear el árbol AST
        root = parse_ast(lines)

        no_declared = []
        with open('salidas/errors.txt', 'r') as file:
            for line in file:
                if(line.startswith("Variable no declarada")):
                    var = line.split("'")[1]
                    no_declared.append(var)

        # Anotar el árbol
        annotate_tree(root, variables, no_declared)

        # Mostrar el árbol anotado
        # print_tree(root, variables)
        
        # Guardar que no hay errores
        with open('salidas/errors.txt', 'w') as file:
            file.write("No errors found\n") 
                   
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
                # Si el tipo de la variable es int y el valor es un flotante, mostrar un error
                if variables[nombre][0] == "int" and isinstance(valor, float):
                    verificarErrores()
                    with open('salidas/errors.txt', 'a') as file:
                        file.write(f"Error: El valor de '{nombre}' debe ser entero, pero es float.\n")
                # Si el tipo de la variable es float y el valor es un entero, guardar con el valor flotante
                elif variables[nombre][0] == "float" and isinstance(valor, int):
                    posicion = parts[4] 
                    update_variable_in_file(nombre, float(valor), parts[4])
                else:
                    update_variable_in_file(nombre, valor, parts[4])