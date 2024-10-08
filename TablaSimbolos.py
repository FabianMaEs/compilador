class LineList:
    def __init__(self, lineno):
        self.lineno = lineno
        self.next = None

class BucketList:
    def __init__(self, name, lineno, loc, var_type, value):
        self.name = name
        self.lines = LineList(lineno)
        self.memloc = loc
        self.var_type = var_type
        self.value = value
        self.next = None

class SymbolTable:
    SIZE = 211

    def __init__(self):
        self.hash_table = [None] * self.SIZE

    def hash(self, key):
        temp = 0
        for char in key:
            temp = ((temp << 5) + ord(char)) % self.SIZE
        return temp

    def insert(self, name, lineno, loc, var_type, value):
        h = self.hash(name)
        bucket = self.hash_table[h]

        while bucket is not None and bucket.name != name:
            bucket = bucket.next

        if bucket is None:  # Variable not in table
            bucket = BucketList(name, lineno, loc, var_type, value)
            bucket.next = self.hash_table[h]
            self.hash_table[h] = bucket
        else:  # Variable found, update value if it's the first assignment
            if bucket.value == "":  # Update value only if it's the first assignment
                bucket.value = value
            line = bucket.lines
            while line.next is not None:
                line = line.next
            line.next = LineList(lineno)

    def print_table(self):
        print("Variable Name  Type     Location   Value   Line Numbers")
        print("-------------  ----     --------   -----   ------------")
        # Create a list to sort by memory location
        all_buckets = []
        for bucket in self.hash_table:
            while bucket is not None:
                all_buckets.append(bucket)
                bucket = bucket.next

        # Sort buckets by memory location
        all_buckets.sort(key=lambda b: b.memloc)

        for bucket in all_buckets:
            line = bucket.lines
            line_numbers = []
            while line is not None:
                line_numbers.append(line.lineno)
                line = line.next
            print(f"{bucket.name:<14} {bucket.var_type:<8} {bucket.memloc:<9} {bucket.value:<8} {', '.join(map(str, line_numbers))}")
    
    def save_table(self):
        with open("salidas/tabla_simbolos.txt", "w") as file:
            all_buckets = []
            for bucket in self.hash_table:
                while bucket is not None:
                    all_buckets.append(bucket)
                    bucket = bucket.next
            all_buckets.sort(key=lambda b: b.memloc)
            for bucket in all_buckets:
                line = bucket.lines
                line_numbers = []
                while line is not None:
                    line_numbers.append(line.lineno)
                    line = line.next
                file.write(f"{bucket.name:<14} {bucket.var_type:<8} {bucket.memloc:<9} {bucket.value:<8} {', '.join(map(str, line_numbers))}\n")


def main():
    symbol_table = SymbolTable()
    loc = 0

    # Lee los tokens desde el archivo
    with open("salidas/output.txt", "r") as file:
        for line in file:
            tokens = line.split()
            token_type = tokens[0]
            value = tokens[1]
            lineno = int(tokens[2])
            colno = int(tokens[3])

            if token_type == "ID":  # Si el token es una variable
                loc += 1  # Incrementa el número de registro
                var_type = "int"  # Puedes personalizar esto según el contexto
                symbol_table.insert(value, lineno, loc, var_type, "")
            elif token_type == "=":  # Si el token es una asignación
                # La variable que se está asignando está en el valor anterior
                variable = tokens[1]
                symbol_table.insert(variable, lineno, loc, var_type, value)

    # Imprime la tabla de símbolos
    symbol_table.print_table()
    symbol_table.save_table()

if __name__ == "__main__":
    main()