from graphviz import Digraph
import os

# Diccionario que mapea tipos de tokens a sus valores esperados
TOKEN_VALUES = {
    "MAS": "+", "MEN": "-", "MUL": "*", "DIV": "/", "POT": "^",
    "MOR": "<", "MAR": ">", "IGU": "=", "NOT": "!", "PYC": ";",
    "COM": ",", "PA": "(", "PC": ")", "LLA": "{", "LLC": "}",
    "NEQ": "!=", "LEQ": "<=", "GEQ": ">=", "AND": "&&", "OR": "||",
    "EQL": "==", "PRO": "program", "IF": "if", "ELS": "else",
    "FI": "fi", "DO": "do", "UNT": "until", "WHI": "while",
    "REA": "read", "WRI": "write", "FLO": "float", "INT": "int",
    "BOO": "bool", "TRU": "true", "FAL": "false", "THN": "then"
}

# Clase para representar un token
class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

# Clase para representar un nodo del AST
class ASTNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

# Clase para analizar el programa y construir el AST
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []  # Lista para almacenar los errores

    # Método para analizar el programa y construir el AST
    def parse_program(self):
        node = ASTNode('program')
        self.match('PRO')
        self.match('LLA')
        node.children.append(self.parse_list_decl())
        node.children.append(self.parse_list_sent())
        self.match('LLC')  # Agregado
        self.match('EOF')
        return node

    # Método para verificar si el token actual es del tipo esperado
    def match(self, token_type):
        if self.current_token().type == token_type:
            self.advance()
        else:
            expected_value = TOKEN_VALUES.get(token_type, token_type)
            error_message = f"Error de sintaxis: Se esperaba '{expected_value}' pero se obtuvo '{self.current_token().value}' en la línea {self.current_token().line} y columna {self.current_token().column}"
            self.errors.append(error_message)
            self.synchronize()  # Intentar recuperar el análisis
            
    def current_token(self):
        return self.tokens[self.current_token_index]

    def advance(self):
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            
    # Método para sincronizar el análisis después de un error
    # Se salta los tokens hasta encontrar un token de sincronización
    def synchronize(self):
        sync_tokens = {'PYC', 'LLC', 'LLA', 'PA', 'PC', 'IF', 'ELS', 'FI', 'DO', 'UNT', 'WHI', 'WRI', 'READ'}
        while self.current_token().type not in sync_tokens and self.current_token().type != 'EOF':
            self.advance()

    def parse_list_decl(self):
        node = ASTNode('list-decl')
        while self.current_token().type in ('INT', 'FLO', 'BOO'):
            node.children.append(self.parse_decl())
        return node

    def parse_decl(self):
        node = ASTNode('decl')
        node.children.append(self.parse_tipo())
        node.children.append(self.parse_list_id())
        self.match('PYC')
        return node

    def parse_tipo(self):
        token = self.current_token()
        if token.type in ('INT', 'FLO', 'BOO'):
            self.advance()
            return ASTNode('tipo', token.value)
        else:
            raise SyntaxError(f"Se esperaba un tipo pero se obtuvo {token.type}")

    def parse_list_id(self):
        node = ASTNode('list-id')
        node.children.append(ASTNode('id', self.current_token().value))
        self.match('ID')
        while self.current_token().type == 'COM':
            self.advance()
            node.children.append(ASTNode('id', self.current_token().value))
            self.match('ID')
        return node

    def parse_list_sent(self):
        node = ASTNode('list-sent')
        while self.current_token().type != 'EOF' and self.current_token().type != 'LLC':
            node.children.append(self.parse_sent())
        return node

    def parse_sent(self):
        token = self.current_token()
        if token.type == 'IF':
            return self.parse_sent_if()
        elif token.type == 'WHI':
            return self.parse_sent_while()
        elif token.type == 'DO':
            return self.parse_sent_do()
        elif token.type == 'READ':
            return self.parse_sent_read()
        elif token.type == 'WRI':
            return self.parse_sent_write()
        elif token.type == 'LLA':
            return self.parse_bloque()
        elif token.type == 'ID':
            return self.parse_sent_assign()
        else:
            raise SyntaxError(f"Token inesperado {token.type}")

    def parse_sent_if(self):
        node = ASTNode('sent-if')
        self.match('IF')
        self.match('PA')
        node.children.append(self.parse_exp_bool())
        self.match('PC')
        self.match('THN')
        node.children.append(self.parse_bloque())
        if self.current_token().type == 'ELS':
            self.match('ELS')
            node.children.append(self.parse_bloque())
        self.match('FI')
        return node

    def parse_sent_while(self):
        node = ASTNode('sent-while')
        self.match('WHI')
        self.match('PA')
        node.children.append(self.parse_exp_bool())
        self.match('PC')
        node.children.append(self.parse_bloque())
        return node

    def parse_sent_do(self):
        node = ASTNode('sent-do')
        self.match('DO')
        node.children.append(self.parse_bloque())
        self.match('UNT')
        self.match('PA')
        node.children.append(self.parse_exp_bool())
        self.match('PC')
        self.match('PYC')
        return node
    
    # Solo imprime identificadores
    def parse_sent_write(self):
        node = ASTNode('sent-write')
        self.match('WRI')
        node.children.append(self.parse_list_id())
        self.match('PYC')
        return node

    def parse_bloque(self):
        node = ASTNode('bloque')
        self.match('LLA')
        node.children.append(self.parse_list_sent())
        self.match('LLC')
        return node

    def parse_sent_assign(self):
        node = ASTNode('sent-assign')
        node.children.append(ASTNode('id', self.current_token().value))
        self.match('ID')
        self.match('IGU')
        node.children.append(self.parse_exp_bool())
        self.match('PYC')
        return node

    def parse_exp_bool(self):
        node = self.parse_comb()
        while self.current_token().type == 'OR':
            op_node = ASTNode('or', 'or')
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_comb())
            node = op_node
        return node

    def parse_comb(self):
        node = self.parse_igualdad()
        while self.current_token().type == 'AND':
            op_node = ASTNode('and', 'and')
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_igualdad())
            node = op_node
        return node

    def parse_igualdad(self):
        node = self.parse_rel()
        while self.current_token().type in ('EQL', 'NEQ'):
            op_node = ASTNode('igualdad', self.current_token().value)
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_rel())
            node = op_node
        return node

    def parse_rel(self):
        node = self.parse_expr()
        if self.current_token().type in ('LEQ', 'GEQ', 'MOR', 'MAR'):
            op_node = ASTNode('rel', self.current_token().value)
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_expr())
            node = op_node
        return node

    def parse_expr(self):
        node = self.parse_term()
        while self.current_token().type in ('MAS', 'MEN'):
            op_node = ASTNode('expr', self.current_token().value)
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_term())
            node = op_node
        return node

    def parse_term(self):
        node = self.parse_unario()
        while self.current_token().type in ('MUL', 'DIV'):
            op_node = ASTNode('term', self.current_token().value)
            self.advance()
            op_node.children.append(node)
            op_node.children.append(self.parse_unario())
            node = op_node
        return node

    def parse_unario(self):
        if self.current_token().type in ('NOT', 'MEN'):
            node = ASTNode('unario', self.current_token().value)
            self.advance()
            node.children.append(self.parse_unario())
            return node
        else:
            return self.parse_factor()

    def parse_factor(self):
        token = self.current_token()
        if token.type == 'PA':
            self.advance()
            node = self.parse_exp_bool()
            self.match('PC')
            return node
        elif token.type in ('ID', 'NUM', 'TRU', 'FAL'):
            self.advance()
            return ASTNode('factor', token.value)
        else:
            raise SyntaxError(f"Token inesperado {token.type}")

# Funciones para visualizar el AST. Si el graph argumento es None, se crea un nuevo gráfico
# y se devuelve el gráfico resultante. De lo contrario, se agrega el nodo actual al gráfico existente.
# Despues de agregar el nodo actual, se llama recursivamente a la función para cada hijo del nodo actual.
def visualize_ast(node, graph=None, parent=None):
    if graph is None:
        graph = Digraph()
        graph.node('root', node.type)
        parent = 'root'

    node_id = str(id(node))
    label = f"{node.type}"
    if node.value is not None:
        label += f" ({node.value})"
    
    graph.node(node_id, label)
    graph.edge(parent, node_id)

    for child in node.children:
        visualize_ast(child, graph, node_id)

    return graph

# Función para serializar el AST en un formato de texto
def serialize_ast(node, level=0):
    lines = []
    indent = '  ' * level
    label = f"{node.type}"
    if node.value is not None:
        label += f" ({node.value})"
    lines.append(indent + label)
    for child in node.children:
        lines.extend(serialize_ast(child, level + 1))
    return lines


# Creación del AST y manejo de errores
# Leer el archivo de tokens
tokens = []
with open('salidas/output.txt', 'r') as file:
    for line in file:
        parts = line.strip().split()
        type = parts[0]
        value = parts[1]
        line = parts[2]
        column = parts[3]
        if type not in ('COC', 'COL'):
            tokens.append(Token(type, value, line, column))

# Añadir el token EOF al final
tokens.append(Token('EOF', 'EOF', 0, 0))

output_path = 'salidas/ast'

try:
    parser = Parser(tokens)
    ast = parser.parse_program()

    # Visualización del AST
    graph = visualize_ast(ast)
    graph.render(output_path, format='png', view=True)

    # Guardar el AST en formato de texto
    ast_text = serialize_ast(ast)
    with open('salidas/ast.txt', 'w') as f:
        f.write('\n'.join(ast_text))

except SyntaxError as e:
    error_message = f"Error de sintaxis: {str(e)} en la línea {parser.current_token().line} y columna {parser.current_token().column} '{parser.current_token().value}'"
    with open('salidas/errors.txt', 'w') as error_file:
        error_file.write(error_message)

# Guardar todos los errores detectados
if parser.errors:
    with open('salidas/errors.txt', 'w') as error_file:
        for error in parser.errors:
            error_file.write(error + '\n')
else:   
    with open('salidas/errors.txt', 'w') as error_file:
        error_file.write("No errors found")

# Verificar si el archivo de gráfico se creó
if os.path.exists(f"{output_path}.png"):
    print(f"Graph successfully created at {output_path}.png")
else:
    print(f"Failed to create graph at {output_path}.png")

# Verificar si el archivo AST se creó
if os.path.exists('salidas/ast.txt'):
    print("AST successfully written to salidas/ast.txt")
else:
    print("Failed to write AST to salidas/ast.txt")

# Verificar si el archivo de errores se creó
if os.path.exists('salidas/errors.txt') and parser.errors:
    print("Errors successfully written to salidas/errors.txt")
else:
    print("No errors found or failed to write errors to salidas/errors.txt")
