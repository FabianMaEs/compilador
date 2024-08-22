import keyword
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

        # Ventana principal dividida en tres partes
        # Código
        # Crea el marco para el código con un color oscuro
        self.code_frame = ttk.Frame(root, width=400, height=500, relief="solid", borderwidth=1, style="clam.TFrame")
        self.code_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        # Configurar el área de texto para el código con resaltado
        self.code_text = tk.Text(self.code_frame, wrap="word", undo=True)   # Habilita el deshacer
        self.code_text.grid(row=0, column=0, sticky="nsew")                       # Expande el widget para llenar el marco
        self.code_text.pack(fill="both", expand=True)
        self.code_text.bind('<KeyRelease>', self.highlight_keywords)    # Resalta las palabras clave al escribir
        
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
        self.output_frame = ttk.Frame(root, width=400, height=500, relief="solid", borderwidth=1)
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

        self.semantic_tab = ttk.Frame(self.analyzer_notebook)
        self.analyzer_notebook.add(self.semantic_tab, text="Semántico")
        
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
        
        # Crear widgets para la pestaña sintáctica gráfica
        if(os.path.exists('salidas/ast.png')):
            # Remove previous image
            for widget in self.syntax_tab_image.winfo_children():
                widget.destroy()
            
            load = Image.open('salidas/ast.png')
            # Redimensionar la imagen
            resized_image = load.resize((500, 500))
            render = ImageTk.PhotoImage(resized_image)
            img = tk.Label(self.syntax_tab_image, image=render)
            img.image = render
            img.pack()
            # Vincular el evento de clic a la función
            img.bind("<Button-1>", self.open_full_image)
        
        # Crear widgets para la pestaña semántica
        self.semantic_text = tk.Text(self.semantic_tab, wrap="word", undo=True)
        self.semantic_text.pack(fill="both", expand=True)
        self.semantic_text.insert(tk.END, "Información semántica...")
        self.semantic_text.config(state=tk.DISABLED)
        
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
        
    def change_color_scheme(self):
        selected_scheme = self.color_scheme.get()
        if selected_scheme == 'light':
            self.code_text.configure(bg='#ffffff', fg='#000000')  # Cambiar a esquema de color claro
            self.lexical_text.configure(bg='#ffffff', fg='#000000')
            self.syntax_text.configure(bg='#ffffff', fg='#000000')
            
            self.semantic_text.configure(bg='#ffffff', fg='#000000')
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

            self.semantic_text.configure(bg='#2b2b2b', fg='#ffffff')
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
        if self.file_path is None or self.file_path == '':
            self.file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            # Lógica para guardar el archivo
            if self.file_path:
                with open(self.file_path, 'w') as file:
                    file.write(self.code_text.get('1.0', tk.END))
                messagebox.showinfo("Guardar archivo", "Archivo guardado exitosamente.")
        else:
            with open(self.file_path, 'w') as file:
                file.write(self.code_text.get('1.0', tk.END))
            messagebox.showinfo("Guardar archivo", "Archivo guardado exitosamente.")

    def highlight_keywords(self, event=None):
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
        
    def help_window(self):
        # Crear una ventana emergente
        help_window = tk.Toplevel()
        help_window.title("Ayuda")
        help_window.aspect(1, 1, 1, 1)
        help_window.geometry("400x400")
        help_window.resizable(False, True)
        
        # Crear un widget Label para mostrar el texto de ayuda
        help_text = tk.Label(help_window, text="Este es un IDE simple creado con Python y Tkinter.\n\n"
                                               "Características:\n"
                                               "- Resaltado de sintaxis\n"
                                               "- Compilación de código Java\n"
                                               "- Análisis léxico y sintáctico\n"
                                               "- Soporte para temas oscuros y claros\n"
                                               "- Atajos de teclado\n"
                                               "- Guardar y abrir archivos\n"
                                               "- Ayuda y documentación\n\n"
                                               "Atajos de teclado:\n"
                                               "- Ctrl + O: Abrir archivo\n"
                                               "- Ctrl + S: Guardar archivo\n"
                                               "- Ctrl + Z: Deshacer\n"
                                               "- Ctrl + Y: Rehacer\n"
                                               "- Ctrl + R: Compilar código\n"
                                               "- Ctrl + Q: Salir\n"
                                               "- Ctrl + Backspace: Eliminar última palabra\n"
                                               "- Ctrl + Delete: Eliminar siguiente palabra\n"
                                               "- Ctrl + H: Ayuda\n")
        help_text.pack()

    def compile_code(self):
        # Directorio donde se encuentran los archivos Java y la clase
        java_dir = 'C:\\Users\\fabma\\UAA\\compilador\\compilador'

        # Cambiar al directorio donde se encuentran los archivos Java y la clase
        os.chdir(java_dir)

        # Guardar el archivo actual en uno temporal antes de compilar
        if self.file_path is None or self.file_path == '':
            self.file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if self.file_path:
                with open(self.file_path, 'w') as file:
                    file.write(self.code_text.get('1.0', tk.END))
        else:
            with open(self.file_path, 'w') as file:
                file.write(self.code_text.get('1.0', tk.END))
        
        # Obtener el nombre del archivo actual
        #file_path = filedialog.asksaveasfilename(defaultextension=".java")
        print("Archivo: " + self.file_path)
        
        # Verificar si el archivo compilado existe
        if not os.path.exists(os.path.join(java_dir, 'Lexer.class')):
            print("Compilando código...")
            try:
                # Compilar el código Java
                subprocess.run(['javac', 'Lexer.java'], check=True)
            except subprocess.CalledProcessError as e:
                print("Error durante la compilación:")
                print(e)
                return

        # Leer el contenido del archivo de entrada
        input_file = self.file_path
        with open(input_file, 'r') as file:
            code = file.read()

        print("Código de entrada:\n" + code)
        
        # Ejecutar el archivo compilado con el nombre del archivo de entrada como argumento
        try:
            result = subprocess.run(['java', 'Lexer', input_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución:")
            print(e)
            return
        
        # Mostrar la salida del programa
        print(result.stdout.strip())
        # Guardar en un archivo de texto
        with open('salidas/output.txt', 'w') as file:
            file.write(result.stdout.strip())
        cadena = result.stdout.strip()
        
        if result.returncode == 0:
            # Habilitar el widget Text para la edición
            self.lexical_text.config(state=tk.NORMAL)
            # Eliminar todo el texto actual en el widget Text
            self.lexical_text.delete('1.0', tk.END)
            # Insertar el nuevo texto en el widget Text
            self.lexical_text.insert(tk.END, cadena)
            # Deshabilitar el widget Text después de insertar el nuevo texto
            self.lexical_text.config(state=tk.DISABLED)
        else:
            print("Error durante la ejecución:")
            print(result.stderr.strip())
            
        # Ejecutar el sintactico.py
        try:
            result = subprocess.run(['python', 'Sintactico funciona.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print("Error durante la ejecución:")
            print(e)
            return
        
        try:
            # Mostrar ast.txt en la pestaña sintáctico
            with open('salidas/ast.txt', 'r') as file:
                analisis_sintactico = file.read()
            self.syntax_text.config(state=tk.NORMAL)
            self.syntax_text.delete('1.0', tk.END)
            self.syntax_text.insert(tk.END, analisis_sintactico)
            self.syntax_text.config(state=tk.DISABLED)
            
            if(os.path.exists('salidas/ast.png')):
                # Remove previous image
                for widget in self.syntax_tab_image.winfo_children():
                    widget.destroy()
                
                load = Image.open('salidas/ast.png')
                # Redimensionar la imagen
                resized_image = load.resize((500, 500))
                render = ImageTk.PhotoImage(resized_image)
                img = tk.Label(self.syntax_tab_image, image=render)
                img.image = render
                img.pack()
                # Vincular el evento de clic a la función
                img.bind("<Button-1>", self.open_full_image)
                
        except:
            print("Error durante la ejecución:")
            print(result.stderr.strip())
        
        # Mostrar salidas/errors.txt en la pestaña de errores
        with open('salidas/errors.txt', 'r') as file:
            errores = file.read()
        self.errors_text.config(state=tk.NORMAL)
        self.errors_text.delete('1.0', tk.END)
        self.errors_text.insert(tk.END, errores)
        self.errors_text.config(state=tk.DISABLED)
        
        # Mostrar la imagen ast.png en la pestaña sintáctico gráfico
    
    def open_full_image(self, event=None):
        # Mostrar la imagen con controles de desplazamiento
        top = tk.Toplevel()
        top.title("Árbol sintáctico")
        
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