import re

# Función para leer el árbol desde un archivo
def leer_arbol(file_path):
    with open(file_path, 'r') as file:
        return [line.rstrip() for line in file.readlines()]

# Función para leer la tabla de símbolos
def leer_tabla_simbolos(file_path):
    tabla = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) >= 4:
                variable = parts[0]
                tipo = parts[1]
                valor = None  # Inicialmente sin valor asignado
                tabla[variable] = {'tipo': tipo, 'valor': valor}
    return tabla

# Función para calcular el valor de una expresión simple
def calcular_expr(factores):
    return sum(factores)

# Función principal para anotar el árbol
def anotar_arbol(arbol, tabla):
    arbol_anotado = []
    current_var = None
    factores_expr = []

    for line in arbol:
        # Busca IDs en el árbol y les agrega el tipo y valor correspondiente
        match_id = re.match(r'\s*id \((\w+)\)', line)
        match_factor = re.match(r'\s*factor \((\d+)\)', line)
        match_expr = re.search(r'expr \((\+)\)', line)

        # Si encuentra un ID, se anota con su tipo y valor en la tabla de símbolos
        if match_id:
            var_name = match_id.group(1)
            current_var = var_name
            if var_name in tabla:
                tipo = tabla[var_name]['tipo']
                valor = tabla[var_name]['valor'] if tabla[var_name]['valor'] is not None else 'N/A'
                arbol_anotado.append(f"{line} [tipo: {tipo} | valor: {valor}]")
            else:
                arbol_anotado.append(line)

        # Si encuentra un factor con valor numérico
        elif match_factor:
            valor = int(match_factor.group(1))
            arbol_anotado.append(f"{line} [valor: {valor}]")
            factores_expr.append(valor)

        # Si encuentra una expresión, calcula el valor de la suma de factores
        elif match_expr:
            resultado_expr = calcular_expr(factores_expr)
            arbol_anotado.append(line + f" [valor: {resultado_expr}]")
            if current_var:
                tabla[current_var]['valor'] = resultado_expr  # Actualizar el valor de la variable asignada
            factores_expr = []  # Reinicia los factores para la siguiente expresión

        # Si es una sentencia de asignación, actualiza el valor correspondiente
        elif "sent-assign" in line:
            if current_var and tabla[current_var]['valor'] is not None:
                tipo = tabla[current_var]['tipo']
                valor = tabla[current_var]['valor']
                arbol_anotado.append(f"{line} [tipo: {tipo} | valor: {valor}]")
            else:
                arbol_anotado.append(line)
        else:
            arbol_anotado.append(line)

    return arbol_anotado

# Guardar el árbol anotado en un archivo
def guardar_arbol_anotado(arbol_anotado, file_path):
    with open(file_path, 'w') as file:
        for line in arbol_anotado:
            file.write(line + '\n')

# Leer los archivos
arbol = leer_arbol('salidas/ast.txt')
tabla_simbolos = leer_tabla_simbolos('salidas/tabla_simbolos.txt')

# Anotar el árbol
arbol_anotado = anotar_arbol(arbol, tabla_simbolos)

# Guardar el árbol anotado
guardar_arbol_anotado(arbol_anotado, 'salidas/arbol_anotado.txt')
