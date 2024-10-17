class Node:
    def __init__(self, nombre, tipo=None, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def __str__(self):
        tipo_str = f" ({self.tipo}: {self.valor})" if self.tipo else ""
        return f"{self.nombre}{tipo_str}"

# Clases especializadas para diferentes tipos de nodos
class OperationNode(Node):
    def __init__(self, nombre, operador):
        super().__init__(nombre)
        self.operador = operador

class FactorNode(Node):
    def __init__(self, nombre, valor):
        super().__init__(nombre, valor=valor)
        self.tipo = 'int' if isinstance(valor, int) else 'float'

class IfNode(Node):
    def __init__(self, nombre):
        super().__init__(nombre)
        
class ComparisonNode(Node):
    def __init__(self, nombre, operador):
        super().__init__(nombre)
        self.operador = operador
        
class ComparisonNode(Node):
    def __init__(self, nombre, operador):
        super().__init__(nombre)
        self.operador = operador
        
class IdentifierNode(Node):
    def __init__(self, nombre, variable):
        super().__init__(nombre)
        self.variable = variable

class DoWhileNode(Node):
    def __init__(self, nombre):
        super().__init__(nombre)

class WhileNode(Node):
    def __init__(self, nombre):
        super().__init__(nombre)

def create_node(line):
    # Detectar el tipo de nodo basado en el nombre
    parts = line.strip().split(' ')
    nombre = parts[0]

    # Verificar si es una operación de comparación
    if len(parts) > 1 and parts[1].strip('()') in ('==', '!=', '<', '<=', '>', '>=', 'and', 'or'):
        operador = parts[1].strip('()')
        return ComparisonNode(nombre, operador)
    elif len(parts) > 1 and parts[1].strip('()') in ('+', '-', '*', '/'):
        operador = parts[1].strip('()')
        return OperationNode(nombre, operador=operador)
    elif nombre.startswith('tipo'):
        tipo = parts[1].strip('()')
        return Node(tipo)
    elif nombre == 'factor':
        valor_str = parts[1].strip('()')
        try:
            valor = float(valor_str) if '.' in valor_str else int(valor_str)
        except ValueError:
            valor = valor_str
        return FactorNode(nombre, valor)
    elif nombre == 'id':
        variable = parts[1].strip('()')
        return IdentifierNode(nombre, variable)
    elif nombre == 'comparacion':
        return Node(nombre)
    elif nombre == 'if':
        return IfNode(nombre)
    elif nombre == 'dowhile':
        return DoWhileNode(nombre)
    elif nombre == 'while':
        return WhileNode(nombre)
    else:
        return Node(nombre)

def parse_ast(file_path):
    root = None
    stack = []
    with open(file_path, 'r') as file:
        for line in file:
            indent_level = line.count('?')
            node = create_node(line.replace('?', '').strip())
            if indent_level == 0:
                root = node
            else:
                while len(stack) > indent_level:
                    stack.pop()
                if stack:
                    stack[-1].hijos.append(node)
            stack.append(node)
    return root

def instanceOf(node):
    if isinstance(node, FactorNode):
        return 'FactorNode'
    elif isinstance(node, OperationNode):
        return 'OperationNode'
    elif isinstance(node, ComparisonNode):
        return 'ComparisonNode'
    elif isinstance(node, IdentifierNode):
        return 'IdentifierNode'
    elif isinstance(node, IfNode):
        return 'IfNode'
    elif isinstance(node, DoWhileNode):
        return 'DoWhileNode'
    elif isinstance(node, WhileNode):
        return 'WhileNode'
    else:
        return 'Node'

def evaluate(node, variables):
    # Si es un nodo factor, verificar si es un identificador en la tabla de símbolos
    if isinstance(node, FactorNode):
        if isinstance(node.valor, str) and node.valor in variables:
            nombreSimbolo = node.valor
            simbolo = variables[node.valor]
            node.tipo = simbolo['tipo']
            node.valor = simbolo['valor']
            node.nombre = f"{node.nombre} ({node.tipo}: {nombreSimbolo}: {node.valor})"
        return

    # Evaluar los hijos primero
    for hijo in node.hijos:
        evaluate(hijo, variables)

    # Evaluar las comparaciones
    if isinstance(node, ComparisonNode):
        if len(node.hijos) == 2:
            factor1 = node.hijos[0]
            factor2 = node.hijos[1]
            operador = node.operador
            
            # Verificar si factor1 es una variable y extraer su valor desde la tabla de símbolos
            if isinstance(factor1, FactorNode) and isinstance(factor1.valor, str):
                if factor1.valor in variables:
                    simbolo = variables[factor1.valor]
                    factor1.tipo = simbolo['tipo']
                    factor1.valor = simbolo['valor']
                else:
                    print(f"Advertencia: La variable '{factor1.valor}' no está definida en la tabla de símbolos.")

            # Verificar si factor2 es una variable y extraer su valor desde la tabla de símbolos
            if isinstance(factor2, FactorNode) and isinstance(factor2.valor, str):
                if factor2.valor in variables:
                    simbolo = variables[factor2.valor]
                    factor2.tipo = simbolo['tipo']
                    factor2.valor = simbolo['valor']
                else:
                    print(f"Advertencia: La variable '{factor2.valor}' no está definida en la tabla de símbolos.")


            # Realizar la comparación solo si ambos factores tienen un valor definido
            # print("Comparando", factor1.valor, "con", factor2.valor) 

            # Realizar la comparación
            if factor1.valor is not None and factor2.valor is not None:
                if operador == '==':
                    resultado = factor1.valor == factor2.valor
                elif operador == '!=':
                    resultado = factor1.valor != factor2.valor
                elif operador == '<':
                    resultado = factor1.valor < factor2.valor
                elif operador == '<=':
                    resultado = factor1.valor <= factor2.valor
                elif operador == '>':
                    resultado = factor1.valor > factor2.valor
                elif operador == '>=':
                    resultado = factor1.valor >= factor2.valor
                elif operador == 'and':
                    resultado = bool(factor1.valor) and bool(factor2.valor)
                elif operador == 'or':
                    resultado = bool(factor1.valor) or bool(factor2.valor)
                else:
                    resultado = False

                # Actualizar el nombre del nodo para mostrar el operador y el resultado (TRUE o FALSE)
                node.nombre = f"comparacion ({operador}) {'TRUE' if resultado else 'FALSE'}"
                node.valor = resultado

    # Propagar el resultado de la comparación a un nodo de tipo 'comparacion'
    if node.nombre == 'comparacion':
        resultado_final = all(hijo.valor for hijo in node.hijos if isinstance(hijo, ComparisonNode))
        node.nombre = f"comparacion {'TRUE' if resultado_final else 'FALSE'}"
        node.valor = resultado_final

    # Evaluar la operación si el nodo es un OperationNode
    if isinstance(node, OperationNode):
        hijo_tipos = [hijo.tipo for hijo in node.hijos if hijo.tipo]
        hijo_valores = [hijo.valor for hijo in node.hijos if hijo.valor is not None]

        # Determinar el tipo del nodo basado en los tipos de los hijos
        if 'float' in hijo_tipos:
            node.tipo = 'float'
        else:
            node.tipo = 'int'

        # Calcular el valor de la operación si hay exactamente dos operandos
        if len(hijo_valores) == 2:
            if node.operador == '+':
                node.valor = hijo_valores[0] + hijo_valores[1]
            elif node.operador == '-':
                node.valor = hijo_valores[0] - hijo_valores[1]
            elif node.operador == '*':
                node.valor = hijo_valores[0] * hijo_valores[1]
            elif node.operador == '/':
                node.valor = hijo_valores[0] / hijo_valores[1] if hijo_valores[1] != 0 else None
                
        if node.tipo == 'int':
            node.valor = int(node.valor)
        
        # Formatear el nombre del nodo para mostrar el tipo, operador y resultado
        node.nombre = f"{node.nombre} ({node.tipo}: {node.operador}: {node.valor})"

    # Propagar el tipo y el valor a los nodos expr o term si tienen un solo hijo
    if node.nombre.startswith(('expr', 'term')) and len(node.hijos) == 1:
        child = node.hijos[0]
        node.tipo = child.tipo
        node.valor = child.valor
        node.operador = child.operador if hasattr(child, 'operador') else None

    # Propagar el tipo y valor al nodo id en sent-assign
    if node.nombre == 'sent-assign' and len(node.hijos) == 2:
        id_node = node.hijos[0]
        expr_node = node.hijos[1]
        # Crear un nodo para id que refleje el tipo y valor de la expresión
        if isinstance(id_node, IdentifierNode) and expr_node.tipo and expr_node.valor is not None:
            # Asignar el tipo desde la tabla de símbolos si está definido
            if id_node.tipo is None and id_node.variable in variables:
                id_node.tipo = variables[id_node.variable]['tipo']
            
            # Verificar si el tipo de la expresión coincide con el tipo del identificador o si se puede convertir
            # print(f"Comparando {id_node.variable} ({id_node.tipo}) con {expr_node.tipo} ({expr_node.valor})")
            if id_node.tipo == expr_node.tipo:
                # Si el tipo del identificador coincide con el de la expresión, actualizar el valor
                id_node.valor = expr_node.valor
                id_node.nombre = f"{id_node.variable} ({id_node.tipo}: {id_node.valor})"
                # Actualizar el valor en la tabla de símbolos
                if id_node.variable in variables:
                    variables[id_node.variable]['valor'] = id_node.valor
            elif id_node.tipo == 'float' and expr_node.tipo == 'int':
                # Si el tipo del identificador es float y el tipo de la expresión es int, permitir la conversión
                id_node.valor = float(expr_node.valor)
                id_node.nombre = f"{id_node.variable} ({id_node.tipo}: {id_node.valor})"
            else:
                # Si los tipos no son compatibles, mostrar un error
                id_node.nombre = f"{id_node.variable} (ERROR: tipo incompatible)"
                print(f"Error: tipo incompatible en la asignación de {id_node.variable}. Esperado {id_node.tipo}, encontrado {expr_node.tipo}.")

def read_symbol_table(file_path):
    variables = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                nombre = parts[0].strip()  # Eliminar espacios en blanco del nombre
                tipo = parts[1].strip()  # Eliminar espacios en blanco del tipo
                valor = float(parts[3]) if '.' in parts[3] else int(parts[3])
                loc = parts[2].strip()
                posicion = parts[4].strip()
                variables[nombre] = {'tipo': tipo, 'valor': valor, 'loc': loc, 'posicion': posicion}
    return variables

def annotate_tree(root, variables):
    evaluate(root, variables)

def save_tree(node, file, indent=0):
    indent_str = '?' * (indent)
    # Mostrar el nombre y detalles del nodo
    if isinstance(node, FactorNode):
        if '(' in node.nombre:
            file.write(f"{indent_str}{node.nombre}\n")
        else:
            tipo_str = 'int' if isinstance(node.valor, int) else 'float'
            file.write(f"{indent_str}{node.nombre} ({tipo_str}: {node.valor})\n")
    elif isinstance(node, OperationNode):
        file.write(f"{indent_str}{node.nombre}\n")
    elif node.nombre.startswith(('expr', 'term')):
        file.write(f"{indent_str}{node.nombre}\n")
    elif isinstance(node, IdentifierNode):
        file.write(f"{indent_str}{node.variable}\n")
    elif node.tipo and node.valor is not None:
        file.write(f"{indent_str}{node.nombre}\n")
    else:
        file.write(f"{indent_str}{node.nombre}\n")
    # Recursivamente guardar los hijos
    for hijo in node.hijos:
        save_tree(hijo, file, indent + 1)

def save_symbol_table(variables, file_path):
    with open(file_path, 'w') as file:
        for nombre, info in variables.items():
            tipo = info['tipo']
            valor = info['valor']
            loc = info['loc']
            posicion = info['posicion']
            file.write(f"{nombre}\t{tipo}\t{loc}\t{valor}\t{posicion}\n")
            
# Ejecutar la TablaSimbolos.py para generar la tabla de símbolos
import os

os.system('python TablaSimbolos.py')

# Evaluar y guardar el árbol
symbol_table = read_symbol_table('salidas/tabla_simbolos.txt')
print("Tabla de símbolos cargada:")
for variable, info in symbol_table.items():
    print(f"{variable}: {info}")
ast_root = parse_ast('salidas/ast.txt')
annotate_tree(ast_root, symbol_table)
with open('salidas/ast_anotado.txt', 'w') as file:
    save_tree(ast_root, file)

print("Árbol anotado guardado en 'salidas/ast_anotado.txt'")
save_symbol_table(symbol_table, 'salidas/tabla_simbolos.txt')