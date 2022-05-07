import tkinter as tk
from tkinter import CENTER, HORIZONTAL, filedialog
from tkinter import scrolledtext as st
from tkinter import messagebox as mb
from tkinter import ttk
import time
import re
import sys
import os
from afd import AFD



scanner_lineas = []
file_lines = []
tokens = []
tokens_clean = []
current_token_index = 0
symbols = {}

nombre_compilador = ''
characters_extraidos = {}
keywords_extraidos = {}
tokens_expreg_extraidos = {}

# https://ssw.jku.at/Research/Projects/Coco/
# https://ssw.jku.at/Research/Projects/Coco/Doc/UserManual.pdf

# Cualquier cosa menos "" ''
ANY_BUT_QUOTES = '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»'

characters = {
    ' ': ' ',
    '"': '"',
    '\'': '\'',
    '/': '/',
    '*': '*',
    '=': '=',
    '.': '.',
    '|': '|',
    '(': '(',
    ')': ')',
    '[': '[',
    ']': ']',
    '{': '{',
    '}': '}',
    'o': '+-',
    's': '@~!#$%^&_;:,<>?',
    'l': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'd': '0123456789',
}

keywords = {
    'COMPILER': 'COMPILER',
    'CHARACTERS': 'CHARACTERS',
    'KEYWORDS': 'KEYWORDS',
    'TOKENS': 'TOKENS',
    'PRODUCTIONS': 'PRODUCTIONS',
    'END': 'END',
    'EXCEPT': 'EXCEPT',
    'ANY': 'ANY',
    'CONTEXT': 'CONTEXT',
    'IGNORE': 'IGNORE',
    'PRAGMAS': 'PRAGMAS',
    'IGNORECASE': 'IGNORECASE',
    'WEAK': 'WEAK',
    'COMMENTS': 'COMMENTS',
    'FROM': 'FROM',
    'NESTED': 'NESTED',
    'SYNC': 'SYNC',
    'IF': 'IF',
    'out': 'out',
    'TO': 'TO',
    'NEWLINE': '\\n',
}

tokens_expreg = {
    'semantic_action': '«(.««a¦"»¦\'»±.»)',
    'comment_block': '«/*««a¦"»¦\'»±*»/',
    'comment': '//««««l¦d»¦s»¦o»¦ »±',
    'char': '«\'«a¦"»±»\'',
    'string': '"«a¦\'»±"',
    'number': 'd«d»±',
    'ident': 'l«l¦d»±',
    'operator': 'o',
    'iteration': '{¦}',
    'option': '[¦]',
    'group': '(¦)',
    'or': '|',
    'final': '.',
    'assign': '=',
    'space': ' ',
}



def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("CocoL files", "*.atg"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo1_ = "./" + filename_splited
    label_file_explorer.configure(text=archivo1_)
    archivo1.set(archivo1_)

def browseFiles2():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("Text files", "*.txt"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo2_ = "./" + filename_splited
    label_file_explorer2.configure(text=archivo2_)
    archivo2.set(archivo2_)

def step():
    window.update_idletasks()
    progress['value'] += 20
    
    time.sleep(1)

def tipo_token(word):
    if word in keywords.values():
        return 'KEYWORD'
    else:
        for token_type, re in tokens_expreg.items():
            if AFD(re.replace('a', ANY_BUT_QUOTES)).accepts(word, characters):
                return token_type
    return 'ERROR'

def centinela(line, line_index):
    analyzed_lines = 1
    line_position = 0
    current_line_recognized_tokens = []
    while line_position < len(line):
        current_token = None
        next_token = None
        avance = 0
        continuar = True
        while continuar:
            if current_token and next_token:
                if current_token['type'] != 'ERROR' and next_token['type'] == 'ERROR':
                    avance -= 1
                    continuar = False
                    break

            if line_position + avance > len(line):
                continuar = False
                break

            if line_position + avance <= len(line):
                current_token = {
                    'type': tipo_token(line[line_position:line_position + avance]),
                    'value': line[line_position:line_position + avance],
                    'line': line_index
                }


            avance += 1

            if line_position + avance <= len(line):
                next_token = {
                    'type': tipo_token(line[line_position:line_position + avance]),
                    'value': line[line_position:line_position + avance],
                    'line': line_index
                }


        line_position = line_position + avance


        if current_token and current_token['type'] != 'ERROR':
            tokens.append(current_token)
            current_line_recognized_tokens.append(current_token)
        else:
            print("ERRORES ", current_token)

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                tokens.append(current_token)

            # Si se llega al final de la linea y no se reconoce ningun token,
            # se agrega la siguiente linea y se vuelve a intentar.
            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                if line_index < len(file_lines) - 1:
                    new_line = line.replace('\\n', ' ') + ' ' + file_lines[line_index + 1].replace('\n', '\\n')
                    line_index += 1
                    analyzed_lines += centinela(new_line, line_index)

    return analyzed_lines

def cambio_simbolos(re):
    cont = 0
    closeK = []
    for pos, char in enumerate(re):
        if char == '{':
            cont += 1
        elif char == '}':
            closeK.append(pos)
            cont -= 1

    if cont != 0:
        return False

    re = re.replace('{', '«')
    re = re.replace('}', '»')
    re = re.replace('|', '¦')

    for i in range(len(closeK)):
        re = re[:closeK[i]+1+i] + '±' + re[closeK[i]+1+i:]

    return re

# pasa los keys de los characters a un solo digito
def formatear_characters(characters):
    options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
    cont = 0
    keys = list(characters.keys())
    for i in range(len(characters)):

        symbols[keys[i]] = options[cont]
        characters[options[cont]] = characters.pop(keys[i])
        cont += 1

    return characters

# pasa los identificadores de los values de los tokens a un solo digito definido en formatear_characters
def formatear_tokens_exp(TOKENS_RE):
    # 'letter {letter|digit} EXCEPT KEYWORDS' ---> 'A«A¦B»±'
    options = ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    for key, val in TOKENS_RE.items():
        value = ''
        for token in val:
            if token["value"] in symbols:
                value += symbols[token["value"]]
            else:
                if token["type"] in ['iteration', 'option', 'group', 'or']:
                    value += token["value"]
                else:
                    for o in options:
                        if o not in list(symbols.values()):
                            symbols[token["value"]] = o
                            value += o
                            characters_extraidos[o] = token["value"].replace('"', '')
                            break

        TOKENS_RE[key] = cambio_simbolos(value)

    return TOKENS_RE

# Genera diccionario de CHARACTERS, TOKENS y KEYWORDS
def generador_diccionario():
    token_index = 0
    while token_index < len(tokens):
        token = tokens[token_index]
        token_index += 1
        if token["type"] == 'space' or token["type"] == 'comment' or token["type"] == 'comment_block':
            continue
        elif token["type"] == 'KEYWORD' and token['value'] == '\\n':
            continue
        if token["value"] == 'EXCEPT':
            token_index += 2
            continue
        else:
            tokens_clean.append(token)

    global nombre_compilador
    nombre_compilador = ''

    global characters_extraidos
    characters_extraidos = {}

    global keywords_extraidos
    keywords_extraidos = {
        'NEWLINE': '\\\\n',
    }

    global tokens_expreg_extraidos
    tokens_expreg_extraidos = {}

    token_index = 0
    while token_index < len(tokens_clean):
        token = tokens_clean[token_index]
        if token["type"] == 'KEYWORD':
            if token["value"] == 'COMPILER':
                nombre_compilador = tokens_clean[token_index + 1]["value"]
            elif token["value"] == 'END':
                if nombre_compilador != tokens_clean[token_index + 1]["value"]:
                    text_area.insert(tk.INSERT, "Error sintáctico: Nombre de archivo no coincide", "\n")
            # Lee toda la seccion de Characters del cocol
            elif token["value"] == 'CHARACTERS':
                count = 0
                character_definition_tokens = []
                character_section_definitions = []
                while True:
                    # Iterate until end of characters section tokens
                    temp_token = tokens_clean[token_index + count + 1]

                    # final es el punto
                    if temp_token["type"] == 'final':
                        # If final token is reached, means that the characters definition is finished
                        character_section_definitions.append(character_definition_tokens)
                        character_definition_tokens = []
                    else:
                        character_definition_tokens.append(temp_token)
                    count += 1

                    # Entra a otra seccion diferente de CHARACTERS
                    if temp_token["value"] in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                # Por toda la expresion antes del punto
                for definition_tokens in character_section_definitions:
                    value = ''
                    token_index_ = 0
                    while token_index_ < len(definition_tokens[2::]):
                        token = definition_tokens[2::][token_index_] #Se ignora el identificador y el =
                        # Un character siempre es un identificador = algo mas
                        # Se evalua todo lo despues del =
                        if token["type"] == 'ident':
                            if token["value"] == 'CHR':
                                value += chr(int(definition_tokens[2::][token_index_ + 2]["value"]))
                            else:
                                value += characters_extraidos[token["value"]]
                        elif token["type"] == 'string':
                            value += token["value"].replace('"', '')

                        token_index_ += 1

                    characters_extraidos[definition_tokens[0]["value"]] = value

            elif token["value"] == 'KEYWORDS' and tokens_clean[token_index + 1]["type"] != 'final':
                count = 0
                keyword_definition_tokens = []
                keyword_section_definitions = []
                while True:
                    temp_token = tokens_clean[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        keyword_section_definitions.append(keyword_definition_tokens)
                        keyword_definition_tokens = []
                    else:
                        keyword_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for definition_tokens in keyword_section_definitions:
                    value = ''
                    for token in definition_tokens[2::]:
                        # No pueden haber identificadores ni char, solo string
                        if token["type"] == 'string':
                            value += token["value"].replace('"', '')

                    keywords_extraidos[definition_tokens[0]["value"]] = value

            elif token["value"] == 'TOKENS':
                count = 0
                token_re_definition_tokens = []
                token_re_section_definitions = []
                while True:
                    temp_token = tokens_clean[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        token_re_section_definitions.append(token_re_definition_tokens)
                        token_re_definition_tokens = []
                    else:
                        token_re_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['TOKENS', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for definition_tokens in token_re_section_definitions:
                    value = []
                    for token in definition_tokens[2::]:
                        if token["type"] == 'ident':
                            if token["value"] not in ['EXCEPT', 'KEYWORDS']:
                                value.append(token)
                        elif token["type"] == 'string':
                            value.append(token)
                        elif token["type"] in ['iteration', 'option', 'group', 'or']:
                            value.append(token)

                    tokens_expreg_extraidos[definition_tokens[0]["value"]] = value
        token_index += 1

    characters_extraidos = formatear_characters(characters_extraidos)
    characters_extraidos[' '] = ' '

    tokens_expreg_extraidos = formatear_tokens_exp(tokens_expreg_extraidos)
    tokens_expreg_extraidos['space'] = ' '

# Lee archivo Cocol/R
def lecutra_cocol():
    entry_file = open(archivo1.get(), 'r')

    entry_file_lines = entry_file.readlines()
    entry_file.close()

    file_lines = entry_file_lines

    cont = 0
    for i in entry_file_lines:
        cont += 1
        cont_com = 0
        regpunto = re.search(r'[\.]$', i)
        if regpunto == None and i != "\n" and cont != 1 and cont != len(entry_file_lines):
            if i.isupper():
                pass
            else:
                text_area.insert(tk.INSERT, f"Error en la línea {cont}: falta el punto. {i}")
            
            for char in i:
                if char == ")":
                    cont_com -= 1
                elif char == "(":
                    cont_com += 1
                if cont_com < 0:
                    break
            if cont_com != 0 or i.count('"') % 2 != 0:
                text_area.insert(tk.INSERT, f"Error en la línea {cont}: falta unas comillas {i}")


    with open(archivo1.get()) as file:
        contents = file.read()

        if "EXCEPT KEYWORDS" in contents:
            count_word = contents.count("KEYWORDS")
            if count_word == 1:
                text_area.insert(tk.INSERT, "Warning: no existe la palabra KEYWORDS en el archivo\n")
                text_area.tag_config("start", foreground="orange")
                text_area.tag_add("start", "1.0", "1.52")
            pass
        if "KEYWORDS" not in contents:
            text_area.insert(tk.INSERT, "Error: no existe la palabra KEYWORDS en el archivo\n")
        if "CHARACTERS" not in contents:
            text_area.insert(tk.INSERT, "Error: no existe la palabra CHARACTERS en el archivo\n")
        if "TOKENS" not in contents:
            text_area.insert(tk.INSERT, "Error: no existe la palabra TOKENS en el archivo\n")
    

    line_index = 0
    while line_index < len(file_lines):
        line = file_lines[line_index].replace('\n', '\\n')
        analyzed_lines = centinela(line, line_index) # Retorna cantidad de lineas analizadas
        line_index += analyzed_lines


    for token in tokens:
        if token['type'] == 'ERROR':
            text_area.insert(tk.INSERT, f"Error en la línea  {token['line']}: {token['value']}\n")
    
def scanner():
    scanner_lineas.append("from afd import AFD")
    scanner_lineas.append("import tkinter as tk")
    scanner_lineas.append("from tkinter import scrolledtext as st")

    scanner_lineas.append("ANY_BUT_QUOTES = '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»'\n")

    scanner_lineas.append("characters = {")
    for key, value in characters_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append("keywords = {")
    for key, value in keywords_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append("tokens_expreg = {")
    for key, value in tokens_expreg_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append("TOKENS = []\n")

    scanner_lineas.append("def tipo_token(word):")
    scanner_lineas.append("    if word in keywords.values():")
    scanner_lineas.append("        return 'KEYWORD'")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        for token_type, re in tokens_expreg.items():")
    scanner_lineas.append("            if AFD(re.replace('a', ANY_BUT_QUOTES)).accepts(word, characters):")
    scanner_lineas.append("                return token_type")
    scanner_lineas.append("    return 'ERROR'\n")


    scanner_lineas.append("def centinela(entry_file_lines, line, line_index):")
    scanner_lineas.append("    analyzed_lines = 1")
    scanner_lineas.append("    line_position = 0")
    scanner_lineas.append("    current_line_recognized_tokens = []")
    scanner_lineas.append("    while line_position < len(line):")
    scanner_lineas.append("        current_token = None")
    scanner_lineas.append("        next_token = None")
    scanner_lineas.append("        avance = 0")
    scanner_lineas.append("        continuar = True")
    scanner_lineas.append("        while continuar:")
    scanner_lineas.append("            if current_token and next_token:")
    scanner_lineas.append("                if current_token['type'] != 'ERROR' and next_token['type'] == 'ERROR':")
    scanner_lineas.append("                    avance -= 1")
    scanner_lineas.append("                    continuar = False")
    scanner_lineas.append("                    break\n")

    scanner_lineas.append("            if line_position + avance > len(line):")
    scanner_lineas.append("                continuar = False")
    scanner_lineas.append("                break\n")

    scanner_lineas.append("            if line_position + avance <= len(line):")
    scanner_lineas.append("                current_token = {")
    scanner_lineas.append("                    'type': tipo_token(line[line_position:line_position + avance]),")
    scanner_lineas.append("                    'value': line[line_position:line_position + avance],")
    scanner_lineas.append("                    'line': line_index")
    scanner_lineas.append("                }")

    scanner_lineas.append("            avance += 1\n")

    scanner_lineas.append("            if line_position + avance <= len(line):")
    scanner_lineas.append("                next_token = {")
    scanner_lineas.append("                    'type': tipo_token(line[line_position:line_position + avance]),")
    scanner_lineas.append("                    'value': line[line_position:line_position + avance],")
    scanner_lineas.append("                    'line': line_index")
    scanner_lineas.append("                }")

    scanner_lineas.append("        line_position = line_position + avance\n\n")


    scanner_lineas.append("        if current_token and current_token['type'] != 'ERROR':")
    scanner_lineas.append("            # print(current_token)")
    scanner_lineas.append("            TOKENS.append(current_token)")
    scanner_lineas.append("            current_line_recognized_tokens.append(current_token)")
    scanner_lineas.append("        else:")
    scanner_lineas.append("            print(current_token)\n")

    scanner_lineas.append("            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:")
    scanner_lineas.append("                TOKENS.append(current_token)\n")

    scanner_lineas.append("            # Si se llega al final de la linea y no se reconoce ningun token,")
    scanner_lineas.append("            # se agrega la siguiente linea y se vuelve a intentar.")
    scanner_lineas.append("            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:")
    scanner_lineas.append("                if line_index < len(entry_file_lines) - 1:")
    scanner_lineas.append("                    new_line = line + ' ' + entry_file_lines[line_index + 1].replace('\\n', '\\\\n')")
    scanner_lineas.append("                    line_index += 1")
    scanner_lineas.append("                    analyzed_lines += centinela(entry_file_lines, new_line, line_index)\n")

    scanner_lineas.append("    return analyzed_lines\n")


    scanner_lineas.append(f"entry_file = open('{archivo2.get()}', 'r')")

    scanner_lineas.append("entry_file_lines = entry_file.readlines()")
    scanner_lineas.append("entry_file.close()\n")

    scanner_lineas.append("# -------------------------------------------------------")
    scanner_lineas.append("# GET TOKENS")
    scanner_lineas.append("# -------------------------------------------------------")
    scanner_lineas.append("line_index = 0")
    scanner_lineas.append("while line_index < len(entry_file_lines):")
    scanner_lineas.append("    line = entry_file_lines[line_index].replace('\\n', '\\\\n')")
    scanner_lineas.append("    analyzed_lines = centinela(entry_file_lines, line, line_index)")
    scanner_lineas.append("    line_index += analyzed_lines\n")

    scanner_lineas.append("print('\\n\\nTokens found:')")
    scanner_lineas.append("for token in TOKENS:")
    scanner_lineas.append("    if token['type'] == 'ERROR':")
    scanner_lineas.append("        print(token)")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        print(token)\n")

    scanner_lineas.append("# -------------------------------------------------------")
    scanner_lineas.append("# GET TOKENS")
    scanner_lineas.append("# -------------------------------------------------------")
    scanner_lineas.append("lexical_errors = False")
    scanner_lineas.append("print('\\n\\nLexical errors:')")
    scanner_lineas.append("for token in TOKENS:")
    scanner_lineas.append("    if token['type'] == 'ERROR':")
    scanner_lineas.append("        print(f'Lexical error on line {token[\"line\"]}: {token[\"value\"]}')")
    scanner_lineas.append("        lexical_errors = True\n")


    # Se muestran los tokens en una nueva ventana
    scanner_lineas.append("window = tk.Tk()")
    scanner_lineas.append("window.title('Tokens')")
    scanner_lineas.append("window.geometry('500x250')  ")
    scanner_lineas.append("text_area = st.ScrolledText(window, width = 60, height = 15, font = ('Times New Roman',15), foreground = 'white')")
    scanner_lineas.append("text_area.grid(column = 1, row = 1, columnspan=2)")

    scanner_lineas.append("for token in TOKENS:")
    scanner_lineas.append("    if token['type'] == 'KEYWORD':")
    scanner_lineas.append("        if token['value'] == '\\\\n':")
    scanner_lineas.append("            text_area.insert(tk.INSERT, '\\n')")
    scanner_lineas.append("        else:")
    scanner_lineas.append("            text_area.insert(tk.INSERT, f'{token[\"value\"]} ', " ")")
    scanner_lineas.append("    elif token['type'] == 'space':")
    scanner_lineas.append("        continue")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        text_area.insert(tk.INSERT, f'{token[\"type\"]} ')")

    scanner_lineas.append("window.mainloop()")

    lex_analyzer = open('scanner.py', 'w+')

    for line in scanner_lineas:
        lex_analyzer.write(line)
        lex_analyzer.write("\n")

def ejecutar_scanner():
    ejecutar_archivo_scanner.set(True)
    button_run_script.grid_forget()
    os.system('pipenv run python3 scanner.py')


window = tk.Tk()

archivo1 = tk.StringVar()
archivo2 = tk.StringVar()

window.title('Analizador Lexico')
window.geometry("500x500")  
# window.config(background = "white")

# Archivo 1
label_file_explorer = tk.Label(window, text = "Seleccione un archivo", width = 20, height = 4, fg = "white")
button_explore = tk.Button(window, text = "Seleccionar archivo", command = browseFiles)

# Archivo 2
label_file_explorer2 = tk.Label(window, text = "Seleccione un archivo", width = 20, height = 4, fg = "white")
button_explore2 = tk.Button(window, text = "Seleccionar archivo", command = browseFiles2)

# Errores
text_area = st.ScrolledText(window, width = 60, height = 8, font = ("Times New Roman",15), foreground = "red")

creador = tk.Label(window, text="Por Gian Luca Rivera", pady=50, anchor="e", justify=CENTER)
progress = ttk.Progressbar(window, orient = HORIZONTAL,length = 100, mode = 'determinate')
  
label_file_explorer.grid(column = 1, row = 1)  
button_explore.grid(column = 2, row = 1)
label_file_explorer2.grid(column = 1, row = 2)  
button_explore2.grid(column = 2, row = 2)
text_area.grid(column = 1, row = 3, columnspan=2)
# text_area.configure(state ='disabled')
creador.grid(column = 1,row = 4, columnspan=2)

# Espera que se suban archivos para continuar
button_explore.wait_variable(archivo1)
button_explore2.wait_variable(archivo2)

creador.grid_forget()
progress.grid(column = 1,row = 4, columnspan=2)
creador.grid(column = 1,row = 5, columnspan=2)

step()

   
step()
lecutra_cocol()

step()
generador_diccionario()

step()
scanner()

step()
ejecutar_archivo_scanner = tk.BooleanVar()
button_run_script = tk.Button(window, text = "Ejecutar scanner", command = ejecutar_scanner)
progress.grid_forget()
button_run_script.grid(column = 1, row = 4, columnspan=2)
creador.grid(column = 1,row = 5, columnspan=2)
button_run_script.wait_variable(ejecutar_archivo_scanner)

answer = mb.askyesno(message="Analizador lexico ejecutado con éxito!\n\n¿Deseas continuar con otro analizador?", title="Ejecución finalizada")
if answer:
    python = sys.executable
    os.execl(python, python, * sys.argv)
else:
    window.destroy()


window.mainloop()