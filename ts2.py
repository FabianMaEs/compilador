def extract_declared_variables(tokens):
    declared_variables = {}
    i = 0
    while i < len(tokens):
        if tokens[i][0] in ("FLO", "INT", "BOO"):
            tipo = tokens[i][1]
            i += 1
            while i < len(tokens) and tokens[i][0] == "ID":
                nombre = tokens[i][1]
                if nombre in declared_variables:
                    # Si el archivo errors.txt empieza con "No errors found", se elimina
                    verificarErrores()
                    if declared_variables[nombre] != tipo:
                        with open('salidas/errors.txt', 'a') as error_file:
                            error_file.write(f"Variable '{nombre}' declarada con un tipo diferente: {tipo}\n")
                    else:
                        with open('salidas/errors.txt', 'a') as error_file:
                            error_file.write(f"Variable '{nombre}' redeclarada con el mismo tipo: {tipo}\n")
                else:
                    declared_variables[nombre] = tipo
                i += 1
                if i < len(tokens) and tokens[i][0] == "COM":
                    i += 1  # Skip the comma
        i += 1
    return declared_variables

def verificarErrores():
    with open('salidas/errors.txt', 'r') as error_file:
        lines = error_file.readlines()
        if lines[0].startswith("No errors found") or lines == []:
            lines = lines[1:]
    with open('salidas/errors.txt', 'w') as error_file:
        error_file.writelines(lines)
        
def extract_used_variables(tokens):
    used_variables = set()
    i = 0
    while i < len(tokens):
        if tokens[i][0] == "ID":
            nombre = tokens[i][1]
            used_variables.add(nombre)
        i += 1
    return used_variables

def find_undeclared_variables(declared_variables, used_variables):
    undeclared_variables = used_variables - set(declared_variables.keys())
    return undeclared_variables

# Leer el archivo output.txt
with open('salidas/output.txt', 'r') as file:
    lines = file.readlines()

# Parsear los tokens
tokens = [line.strip().split('\t') for line in lines]

# Extraer las declaraciones de variables
try:
    declared_variables = extract_declared_variables(tokens)
    print("Declared Variables:", declared_variables)
except ValueError as e:
    print(e)
    declared_variables = {}

# Extraer las variables utilizadas
used_variables = extract_used_variables(tokens)
print("Used Variables:", used_variables)

# Encontrar las variables no declaradas
undeclared_variables = find_undeclared_variables(declared_variables, used_variables)
print("Undeclared Variables:", undeclared_variables)

# Verificar en el archivo salidas/output.txt si el token ID y la variable no declarada existe y extraer la línea
verificarErrores()
with open('salidas/errors.txt', 'a') as error_file:
    for variable in undeclared_variables:
        for token in tokens:
            if token[0] == "ID" and token[1] == variable:
                error_file.write(f"Variable no declarada: '{variable}' en la línea {token[2]}\n")
                break