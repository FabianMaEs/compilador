import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
import subprocess
from tkinter import messagebox
from PIL import Image, ImageTk

def run_code(message):
    print(message)

class IDE():
    def __init__(self, root):
        self.root = root
        root.title("IDE")
        # pantalla completa
        root.state('zoomed')
        # Configura el estilo ttk con un tema oscuro
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Puedes experimentar con otros temas (aquí uso 'clam' como ejemplo)
        
        self.file_path = None

        # Crea la barra de menú
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir   (Ctrl + O)", command=self.open_file)
        file_menu.add_command(label="Guardar (Ctrl + S)", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Salir   (Ctrl + Q)", command=root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Deshacer (Ctrl + Z)", command=self.undo)
        edit_menu.add_command(label="Rehacer  (Ctrl + Y)", command=self.redo)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Vista", menu=view_menu)

        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="Compilar (Ctrl + R)", command=self.compile_code)
        menubar.add_cascade(label="Compilar", menu=compile_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Ayuda (Ctrl + H)", command=self.help_window)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        root.config(menu=menubar)

        # Marco para el código
        self.code_frame = ttk.Frame(root, width=400, height=800, relief="solid", borderwidth=1, style="clam.TFrame")
        self.code_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Área para los números de línea
        self.line_numbers = tk.Text(self.code_frame, width=4, padx=5, takefocus=0, border=0, background='lightgray', state='disabled', wrap="none", font=('Consolas', 14))
        self.line_numbers.pack(side="left", fill="y")
        
        # Área de texto para el código
        self.code_text = tk.Text(self.code_frame, wrap="word", undo=True)  # Habilita el deshacer
        self.code_text.pack(side="left", fill="both", expand=True)  # Hacer que el widget Text llene el espacio del marco
        
        # Abrir el archivo ejemplos/prueba.txt en el editor
        try: 
            with open('ejemplos/prueba.txt', 'r') as file:
                self.code_text.insert(tk.END, file.read())
                self.apply_highlight()
        except:
            print("Error al abrir el archivo de ejemplo")
            pass
        
        # Tabulación inteligente
        self.code_text.config(tabs=('1c'))
        
        self.code_text.bind('<KeyRelease>', self.highlight_keywords) # Resaltar las palabras clave
        
        # Sincronizar el scroll de ambos widgets
        self.code_text.bind('<MouseWheel>', self.on_mouse_wheel)
        self.line_numbers.bind('<MouseWheel>', self.on_mouse_wheel)
        self.code_text.bind('<Configure>', self.update_line_numbers)  # Cuando cambia el tamaño de la ventana

        # Inicializar los números de línea
        self.update_line_numbers()        
        
        self.font_family = tk.StringVar()
        self.font_size = tk.StringVar()
        self.color_scheme = tk.StringVar()
        
        self.font_family.set('Consolas')
        self.font_size.set('14')
        self.code_text.configure(font=(self.font_family.get(), int(self.font_size.get())))
        
        # Menú desplegable para la fuente
        font_menu = tk.Menu(menubar, tearoff=0)
        font_menu.add_radiobutton(label="Consolas", variable=self.font_family, value='Consolas', command=self.change_font)
        font_menu.add_radiobutton(label="Arial", variable=self.font_family, value='Arial', command=self.change_font)
        font_menu.add_radiobutton(label="Times New Roman", variable=self.font_family, value='Times New Roman', command=self.change_font)
        view_menu.add_cascade(label="Fuente", menu=font_menu)

        # Menú desplegable para el tamaño de la fuente
        size_menu = tk.Menu(menubar, tearoff=0)
        size_menu.add_radiobutton(label="10", variable=self.font_size, value='10', command=self.change_font)
        size_menu.add_radiobutton(label="12", variable=self.font_size, value='12', command=self.change_font)
        size_menu.add_radiobutton(label="14", variable=self.font_size, value='14', command=self.change_font)
        view_menu.add_cascade(label="Tamaño", menu=size_menu)
        
        # Menú desplegable para el esquema de color
        color_menu = tk.Menu(menubar, tearoff=0)
        color_menu.add_radiobutton(label="Claro", variable=self.color_scheme, value='light', command=self.change_color_scheme)
        color_menu.add_radiobutton(label="Oscuro", variable=self.color_scheme, value='dark', command=self.change_color_scheme)
        view_menu.add_cascade(label="Tema", menu=color_menu)

        # Analizador
        self.analyzer_frame = ttk.Frame(root, width=200, height=500, relief="solid", borderwidth=1)
        self.analyzer_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Salida
        self.output_frame = ttk.Frame(root, width=200, height=500, relief="solid", borderwidth=1)
        self.output_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Configurar el gestor de geometría de la ventana principal
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)  # Nuevo row para la salida

        # Crear pestañas para el analizador y la salida
        self.analyzer_notebook = ttk.Notebook(self.analyzer_frame)
        self.analyzer_notebook.pack(fill="both", expand=True)

        self.lexical_tab = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.lexical_tab, text="Léxico")

        self.syntax_tab = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.syntax_tab, text="Sintáctico")
        
        self.syntax_tab_image = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.syntax_tab_image, text="Sintáctico gráfico")

        # Crear la pestaña semántica
        self.semantic_tab = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.semantic_tab, text="Semántico anotaciones")
        
        # Crear un Treeview
        self.tree_semantic = ttk.Treeview(self.semantic_tab)
        self.tree_semantic.pack(fill="both", expand=True)

        # Agregar una barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.semantic_tab, orient="vertical", command=self.tree_semantic.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_semantic.configure(yscrollcommand=scrollbar.set)

        # Crear un marco para la tabla de símbolos
        self.symbol_table = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.symbol_table, text="Tabla de símbolos")

        # Crear el Treeview para la tabla de símbolos
        self.tree_table = ttk.Treeview(self.symbol_table, columns=("Identificador", "Tipo", "Número", "Valor", "Posiciones"), show="headings")
        
        # Definir los encabezados de la tabla
        self.tree_table.heading("Identificador", text="Identificador")
        self.tree_table.heading("Tipo", text="Tipo")
        self.tree_table.heading("Número", text="Número")
        self.tree_table.heading("Valor", text="Valor")
        self.tree_table.heading("Posiciones", text="Posiciones")

        # Definir el ancho de las columnas
        self.tree_table.column("Identificador", width=100)
        self.tree_table.column("Tipo", width=50)
        self.tree_table.column("Número", width=50)
        self.tree_table.column("Valor", width=100)
        self.tree_table.column("Posiciones", width=150)

        # Agregar el Treeview a la interfaz
        self.tree_table.pack(expand=True, fill='both')
        
        self.intermediate_tab = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.intermediate_tab, text="Código intermedio")
        
        self.output_notebook = ttk.Notebook(self.output_frame)
        self.output_notebook.pack(fill="both", expand=True)

        self.errors_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.errors_tab, text="Errores")

        self.results_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.results_tab, text="Resultados")
        
        ## Configurar la información de las pestañas
        
        # Crear widgets para la pestaña léxica
        # Crear una instancia de ttk.Label
        self.lexical_text = tk.Text(self.lexical_tab, wrap="word", undo=True)  # Crear un widget Text
        self.lexical_text.pack(fill="both", expand=True)  # Hacer que el widget Text llene el espacio de la pestaña
        # Configurar el texto en el widget Text
        self.lexical_text.insert(tk.END, "Información léxica...")
        self.lexical_text.config(state=tk.DISABLED)  # Hacer que el texto no sea editable     
        
        # Crear widgets para la pestaña sintáctica
        self.syntax_text = tk.Text(self.syntax_tab, wrap="word", undo=True)
        self.syntax_text.pack(fill="both", expand=True)
        self.syntax_text.insert(tk.END, "Información sintáctica...")
        self.syntax_text.config(state=tk.DISABLED)
        
        # Crear widgets para la pestaña de código intermedio
        self.intermediate_text = tk.Text(self.intermediate_tab, wrap="word", undo=True)
        self.intermediate_text.pack(fill="both", expand=True)
        self.intermediate_text.insert(tk.END, "Código intermedio...")
        self.intermediate_text.config(state=tk.DISABLED)
        
        # Crear widgets para la pestaña de errores
        self.errors_text = tk.Text(self.errors_tab, wrap="word", undo=True)
        self.errors_text.pack(fill="both", expand=True)
        self.errors_text.insert(tk.END, "Errores...")
        self.errors_text.config(state=tk.DISABLED)
        
        # Crear widgets para la pestaña de resultados
        self.results_text = tk.Text(self.results_tab, wrap="word", undo=True)
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert(tk.END, "Resultados...")
        self.results_text.config(state=tk.DISABLED)
        
        self.color_scheme.set('dark')
        self.change_color_scheme()

    def on_mouse_wheel(self, event):
        self.code_text.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    # Sincronizar el desplazamiento de ambos widgets
    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.code_text.yview()[0])
        self.line_numbers.update_idletasks() # Actualizar los números de línea
        self.update_line_numbers()
        
    # Actualizar los números de línea
    def update_line_numbers(self, event=None):
        line_numbers_content = "\n".join(str(i) for i in range(1, int(self.code_text.index('end-1c').split('.')[0])))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_content)
        self.line_numbers.config(state='disabled')
          
    def change_color_scheme(self):
        selected_scheme = self.color_scheme.get()
        if selected_scheme == 'light':
            self.code_text.configure(bg='#ffffff', fg='#000000')  # Cambiar a esquema de color claro
            self.lexical_text.configure(bg='#ffffff', fg='#000000')
            self.syntax_text.configure(bg='#ffffff', fg='#000000')
            
            self.intermediate_text.configure(bg='#ffffff', fg='#000000')
            self.errors_text.configure(bg='#ffffff', fg='#000000')
            self.results_text.configure(bg='#ffffff', fg='#000000')
            self.code_text.tag_configure('keyword', foreground='blue')          # Cambia el color a azul para palabras clave
            self.code_text.tag_configure('datatype', foreground='#007acc')      # Cambia el color para palabras clave: declaraciones
            self.code_text.tag_configure('symbol', foreground='#ff0000')      # Cambia el color para símbolos
            self.code_text.tag_configure('string', foreground='#008000')      # Cambia el color para cadenas
            self.code_text.tag_configure('comment', foreground='#808080')      # Cambia el color para comentarios
            self.code_text.configure(insertbackground='black')
        elif selected_scheme == 'dark':
            self.code_text.configure(bg='#2b2b2b', fg='#ffffff')  # Cambiar a esquema de color oscuro
            self.lexical_text.configure(bg='#2b2b2b', fg='#ffffff')
            self.syntax_text.configure(bg='#2b2b2b', fg='#ffffff')

            self.intermediate_text.configure(bg='#2b2b2b', fg='#ffffff')
            self.errors_text.configure(bg='#2b2b2b', fg='#ffffff')
            self.results_text.configure(bg='#2b2b2b', fg='#ffffff')
            self.code_text.tag_configure('keyword', foreground='#66D9EF')          # Cambia el color para palabras clave
            self.code_text.tag_configure('datatype', foreground='#A6E22E')      # Cambia el color para palabras clave: declaraciones
            self.code_text.tag_configure('symbol', foreground='#F92672')      # Cambia el color para símbolos
            self.code_text.tag_configure('string', foreground='#E6DB74')      # Cambia el color para cadenas
            self.code_text.tag_configure('comment', foreground='#75715E')      # Cambia el color para comentarios
            self.code_text.configure(insertbackground='white')
        
    def open_file(self):
        file_path = filedialog.askopenfilename()
        # Lógica para abrir el archivo seleccionado
        if file_path:
            with open(file_path, 'r') as file:
                self.code_text.delete('1.0', tk.END)  # Limpiar el widget antes de escribir
                self.code_text.insert(tk.END, file.read())
                self.highlight_keywords()

    def save_file(self):
        # Si no hay un archivo ya abierto, pedir la ubicación para guardar
        if not self.file_path:  # Comprobar si file_path está vacío o es None
            self.file_path = filedialog.asksaveasfilename(defaultextension=".txt")

        # Si se ha seleccionado una ubicación (file_path no está vacío)
        if self.file_path:
            try:
                with open(self.file_path, 'w') as file:
                    file.write(self.code_text.get('1.0', tk.END))
                # messagebox.showinfo("Guardar archivo", "Archivo guardado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")


    def highlight_keywords(self, event=None):
        self.update_line_numbers()
        self.root.after(10, self.apply_highlight)

    def apply_highlight(self):
        start_index = '1.0'
        end_index = tk.END
        code = self.code_text.get(start_index, end_index)
        declarations = ['program', 'int', 'float', 'double', 'char', 'string', 'bool', 'print', 'if', 'else', 'fi', 'do', 'until', 'while', 'read', 'write', 'true', 'false', 'then']
        # keywords = keyword.kwlist + declarations  # Agregar más palabras
        keywords = declarations
        
        for word in keywords:
            start_pos = '1.0'
            while True:
                # Escapa los caracteres especiales en el patrón de búsqueda
                escaped_word = re.escape(word)
                start_pos = self.code_text.search(escaped_word, start_pos, stopindex=tk.END, nocase=1, regexp=1)
                if not start_pos:
                    break
                end_pos = f'{start_pos}+{len(word)}c'

                # Asigna colores para palabras clave específicas
                if word in declarations:
                    self.code_text.tag_add('datatype', start_pos, end_pos)
                else:
                    self.code_text.tag_add('keyword', start_pos, end_pos)

                start_pos = end_pos

        start_index = '1.0'
        for char in code:
            # Asignar colores según el carácter
            color_tag = 'symbol' if char in ['+', '-', '*', '/', '^', '<', '<=', '>', '>=', '==', '!=', '=', ';', ',', '(', ')', '{', '}'] else None
            if color_tag:
                self.code_text.tag_add(color_tag, start_index, f'{start_index}+1c')

            start_index = f'{start_index}+1c'
        
        # Expresión regular para encontrar cadenas entre comillas
        string_pattern = r'"([^"\\]|\\.)*"'
        
        # Expresión regular para encontrar cadenas entre comillas simples
        string_pattern += r"|'([^'\\]|\\.)*'"
        
        # Expresión regular para encontrar comentarios de una línea
        comment_pattern = r"|//.*"
        
        # Expresión regular para encontrar comentarios de varias líneas
        comment_pattern += r"|/\*([^*]|\*[^/])*\*/"

        # Asignar colores a las cadenas y comentarios
        for match in re.finditer(string_pattern, code):
            start_pos = f'1.0+{match.start()}c'
            end_pos = f'1.0+{match.end()}c'
            self.code_text.tag_add('string', start_pos, end_pos)
        
        for match in re.finditer(comment_pattern, code):
            start_pos = f'1.0+{match.start()}c'
            end_pos = f'1.0+{match.end()}c'
            self.code_text.tag_add('comment', start_pos, end_pos)
            
        # Configurar atajos de teclado para Undo y Redo
        root.bind('<Control-z>', self.undo)
        root.bind('<Control-y>', self.redo)
        # Configurar atajos para abrir y guardar archivos
        root.bind('<Control-o>', lambda e: self.open_file())
        root.bind('<Control-s>', lambda e: self.save_file())
        # Configurar atajos para eliminar una palabra con Control + Backspace
        root.bind('<Control-BackSpace>', self.delete_last_word)
        root.bind('<Control-Delete>', self.delete_next_word)
        # Configurar atajo para compilar
        root.bind('<Control-r>', lambda e: self.compile_code())
        # Configurar atajo para ayuda
        root.bind('<Control-h>', lambda e: self.help_window())
        # Configurar atajo para salir
        root.bind('<Control-q>', lambda e: root.quit())
        # Configurar atajo para cambiar el tema
        root.bind('<Control-t>', lambda e: self.change_color_scheme())

    def delete_last_word(self, event=None):
        current_line = self.code_text.get("insert linestart", "insert lineend")
        words = current_line.split()
        if words:
            last_word = words[-1]
            start_index = self.code_text.search(last_word, "insert", backwards=True, regexp=True)
            if start_index:
                end_index = f"{start_index}+{len(last_word)}c"
                self.code_text.delete(start_index, end_index)
                
    def delete_next_word(self, event=None):
        current_line = self.code_text.get("insert linestart", "insert lineend")
        words = current_line.split()
        if words:
            first_word = words[0]
            escaped_word = re.escape(first_word)
            start_index = self.code_text.search(escaped_word, "insert", regexp=True)
            if start_index:
                end_index = f"{start_index}+{len(first_word)}c"
                self.code_text.delete(start_index, end_index)

              
    def undo(self, event=None):
        self.code_text.event_generate("<<Undo>>")
        return "break"

    def redo(self, event=None):
        self.code_text.event_generate("<<Redo>>")
        return "break"

    def change_font(self):
        self.code_text.configure(font=(self.font_family.get(), int(self.font_size.get())))
        self.line_numbers.configure(font=(self.font_family.get(), int(self.font_size.get())))
        
    def help_window(self):
        # Crear una ventana emergente
        help_window = tk.Toplevel()
        help_window.title("Ayuda")
        help_window.aspect(1, 1, 1, 1)
        help_window.geometry("400x400")
        help_window.resizable(False, True)
        
        # Extraer el texto de help.txt permitiendo la codificación UTF-8
        with open('help.txt', 'r', encoding='utf-8') as file:
            help_text = file.read()
        
        # Crear un widget Label para mostrar el texto de ayuda
        help_text = tk.Label(help_window, text=help_text, justify=tk.LEFT, wraplength=400, padx=10, pady=10)
        help_text.pack()

    def compile_code(self):
        # Directorio donde se encuentran los archivos Java y la clase
        java_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Cambiar al directorio de trabajo
        os.chdir(java_dir)

        # Guardar el archivo actual
        self.save_file()
        
        print("Archivo: " + self.file_path)

        # Verificar y compilar el archivo Lexer.java
        if not os.path.exists(os.path.join(java_dir, 'Lexer.class')):
            print("Compilando código...")
            try:
                subprocess.run(['javac', 'Lexer.java'], check=True)
            except subprocess.CalledProcessError as e:
                print("Error durante la compilación:")
                print(e)
                return

        # Leer el contenido del archivo de entrada
        print("Leyendo archivo...")
        with open(self.file_path, 'r') as file:
            code = file.read()

        # Ejecutar el análisis léxico
        print("Ejecutando análisis léxico...")
        try:
            result = subprocess.run(['java', 'Lexer', self.file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución (léxico):")
            print(e)
            return

        # Crear directorio de salida si no existe
        output_dir = os.path.join(java_dir, 'salidas')
        os.makedirs(output_dir, exist_ok=True)

        # Limpiar archivos de salida
        for filename in ['output.txt', 'errors.txt', 'ast.txt']:
            with open(os.path.join(output_dir, filename), 'w') as file:
                if filename == 'errors.txt':
                    file.write("No errors found")
                else:
                    file.write("")

        
        # Guardar la salida del análisis léxico
        output_file = os.path.join(output_dir, 'output.txt')
        with open(output_file, 'w') as file:
            file.write(result.stdout.strip())
        
        cadena = result.stdout.strip()
        
        # Verificar si el análisis léxico fue exitoso
        if result.returncode == 0:
            print("Análisis léxico exitoso")
            self.update_text_widget(self.lexical_text, cadena)
        else:
            print("Error durante la ejecución (léxico):")
            print(result.stderr.strip())

        # Ejecutar el análisis sintáctico
        print("Ejecutando Sintactico.py")
        try:
            result = subprocess.run(['python', 'Sintactico.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Ejecutando análisis sintáctico...")
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución (sintáctico):")
            print(e)
            return

        # Leer errores del análisis sintáctico
        with open('salidas/errors.txt', 'r') as file:
            errores = file.read()

        # Mostrar errores en la pestaña correspondiente
        print("Archivo de errores creado")
        self.update_text_widget(self.errors_text, errores)
        
        if errores.startswith("Error") or errores.startswith("Variable"):
            print("Error durante el análisis sintáctico:")
            self.verificarError()
            self.clear_syntax_image()
        else:
            # Mostrar análisis sintáctico y gráfico
            self.display_syntax_analysis()

            # Ejecutar TablaSimbolos.py
            #print("Ejecutando TablaSimbolos.py")
            #self.run_table_symbols_analysis()

            # Ejecutar SemanticoAnotaciones.py
            print("Ejecutando SemanticoAnotaciones.py")
            self.run_semantic_annotations_analysis()

    def clear_syntax_image(self):
        """Eliminar la imagen del análisis sintáctico si existe."""
        if os.path.exists('salidas/ast.png'):
            for widget in self.syntax_tab_image.winfo_children():
                widget.destroy()


    def display_syntax_analysis(self):
        """Mostrar el análisis sintáctico y su representación gráfica."""
        with open('salidas/ast.txt', 'r') as file:
            analisis_sintactico = file.read()
        # Reemplazar los caracteres de mayor que con espacios
        analisis_sintactico = analisis_sintactico.replace('?', ' ')
        self.update_text_widget(self.syntax_text, analisis_sintactico)

        if os.path.exists('salidas/ast.png'):
            self.clear_syntax_image()
            print("Análisis sintáctico gráfico exitoso")
            load = Image.open('salidas/ast.png')
            resized_image = load.resize((500, 500))
            render = ImageTk.PhotoImage(resized_image)
            img = tk.Label(self.syntax_tab_image, image=render)
            img.image = render
            img.pack()
            img.bind("<Button-1>", self.open_full_image)


    """def run_table_symbols_analysis(self):
        
        try:
            result = subprocess.run(['python', 'TablaSimbolos.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Ejecutando análisis de la tabla de símbolos...")
            self.update_symbol_table(result)
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución (tabla de símbolos):")
            print(e)"""


    def run_semantic_annotations_analysis(self):
        """Ejecutar el análisis semántico con anotaciones."""
        try:
            subprocess.run(['python', 'SemanticoAnotaciones.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Ejecutando análisis semántico con anotaciones...")
            self.update_semantic_analysis()
            self.update_symbol_table()
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución (semántico):")
            print(e)

    def update_semantic_analysis(self):
        """Actualizar el widget semántico con el resultado de la ejecución."""
        with open('salidas/errors.txt', 'r') as file:
            errores = file.read()
        if errores.startswith("Error") or errores.startswith("Variable no declarada") or errores.startswith("Variable '"):
            print("Error durante el análisis semántico:")
            self.verificarError()
        else:
            with open('salidas/ast_anotado.txt', 'r') as file:
                analisis_semantico = file.read()
                
            # Reiniciar el Treeview
            self.tree_semantic.delete(*self.tree_semantic.get_children())
            self.add_tree_nodes(analisis_semantico.strip().splitlines())
            
            self.open_tree_branch()
            
    def open_tree_branch(self, event=None):
        """Abrir todas las ramas del árbol recursivamente."""
        def open_recursive(item):
            # Abrir el nodo actual
            self.tree_semantic.item(item, open=True)
            # Llamar recursivamente para cada hijo
            for child in self.tree_semantic.get_children(item):
                open_recursive(child)

        # Iniciar el proceso recursivo en cada elemento de primer nivel
        for item in self.tree_semantic.get_children():
            open_recursive(item)

            
    def add_tree_nodes(self, lines):
        # Crear un diccionario para almacenar los nodos y su ID
        node_ids = {}

        for line in lines:
            level = line.count('?')
            node_name = line.strip().replace('?', '').strip()

            # Filtrar los nodos "program", "list-decl" y "decl"
            if node_name in ["program", "list-decl", "decl"]:
                continue

            # Agregar el nodo a la Treeview
            if level == 0:
                node_id = self.tree_semantic.insert("", "end", text=node_name)
            else:
                # Verificar si el nivel superior existe antes de acceder
                if level - 1 in node_ids:
                    parent_id = node_ids[level - 1]
                    node_id = self.tree_semantic.insert(parent_id, "end", text=node_name)
                else:
                    # Si no existe, puedes optar por insertar el nodo en la raíz
                    # o manejarlo de otra manera. Aquí lo insertamos como raíz
                    node_id = self.tree_semantic.insert("", "end", text=node_name)

            # Almacenar el ID del nodo actual
            node_ids[level] = node_id
        
    def verificarError(self):
        # Mensaje de error a mostrar
        error_message = "Error durante el análisis. Revise la pestaña de errores."

        # Aplicar la función a cada widget
        self.update_text_widget(self.syntax_text, error_message)
        #self.update_text_widget(self.semantic_tab, error_message)
        self.update_text_widget(self.intermediate_text, error_message)
        self.update_text_widget(self.errors_text, open('salidas/errors.txt', 'r').read())
        for widget in self.syntax_tab_image.winfo_children():
            widget.destroy()
                
    def update_text_widget(self, widget, message):
        widget.config(state=tk.NORMAL)
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, message)
        widget.config(state=tk.DISABLED)
        
    def update_symbol_table(self):
        # Reiniciar el Treeview
        self.tree_table.delete(*self.tree_table.get_children())
        # Cargar los datos en la tabla de símbolos
        self.load_symbol_table("salidas/tabla_simbolos.txt")
        
    def update_symbol_table_error(self):
        # Reiniciar el Treeview
        self.tree_table.delete(*self.tree_table.get_children())
        # Cargar los datos en la tabla de símbolos
        # Mostrar un mensaje de error
        self.tree_table.insert("", "end", values=("Error", "Error", "Error", "Error", "Error"))

    def load_symbol_table(self, filename):
        print("Cargando tabla de símbolos...")
        with open(filename, "r") as file:
            for line in file:
                # Separar las columnas por tabulaciones
                columns = line.strip().split("\t")
                # Insertar la fila en el Treeview
                self.tree_table.insert("", "end", values=columns)

    
    def open_full_image(self, event=None):
        print("Abriendo imagen...")
        # Mostrar la imagen con controles de desplazamiento
        top = tk.Toplevel()
        top.title("Árbol sintactico")
        
        # Crear un Canvas para mostrar la imagen
        canvas = tk.Canvas(top)
        canvas.pack(fill="both", expand=True)
        # Tamaño de la imagen
        canvas.config(width=700, height=500)
        
        # Cargar la imagen
        load = Image.open('salidas/ast.png')
        self.render = ImageTk.PhotoImage(load)  # Mantener la referencia
        canvas.create_image(0, 0, anchor="nw", image=self.render)
        
        # Crear un control de desplazamiento horizontal para el Canvas
        scroll = tk.Scrollbar(top, orient="horizontal", command=canvas.xview)
        scroll.pack(side="bottom", fill="x")
        canvas.config(xscrollcommand=scroll.set)
        
        # Permitir el desplazamiento con el ratón
        canvas.bind("<ButtonPress-1>", lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind("<B1-Motion>", lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
        
        # Configurar el área de desplazamiento del Canvas
        canvas.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))
        
                
    def run_code(self):
        code = self.code_text.get('1.0', tk.END)
        run_code(code)
        
if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()