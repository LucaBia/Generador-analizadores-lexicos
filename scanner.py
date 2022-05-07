from afd import AFD
import tkinter as tk
from tkinter import scrolledtext as st 

characters = {
    'A': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'B': '01234567890',
    'C': '01234567890ABCDEF',
    'D': '	',
    ' ': ' ',
    'S': 'H',
}

keywords = {
    'NEWLINE': '\\n',
    'si': 'if',
    'SI': 'IF',
    'para': 'for',
}

tokens_expreg = {
    'identificador': 'A«A¦B»±',
    'numero': 'B«B»±',
    'numeroHex': 'C«C»±S',
    'tabulador': 'D',
    'space': ' ',
}

tokens = []

def tipo_token(word):
    if word in keywords.values():
        return 'KEYWORD'
    else:
        for token_type, re in tokens_expreg.items():
            if AFD(re.replace('a', '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»')).accepts(word, characters):
                return token_type
    return 'ERROR'

def centinela(entry_file_lines, line, line_index):
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
            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                tokens.append(current_token)

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                if line_index < len(entry_file_lines) - 1:
                    new_line = line + ' ' + entry_file_lines[line_index + 1].replace('\n', '\\n')
                    line_index += 1
                    analyzed_lines += centinela(entry_file_lines, new_line, line_index)

    return analyzed_lines

entry_file = open('./ArchivoPrueba2Entrada.txt', 'r')
entry_file_lines = entry_file.readlines()
entry_file.close()

line_index = 0
while line_index < len(entry_file_lines):
    line = entry_file_lines[line_index].replace('\n', '\\n')
    analyzed_lines = centinela(entry_file_lines, line, line_index)
    line_index += analyzed_lines

for token in tokens:
    if token['type'] == 'ERROR':
        print(f'Lexical error on line {token["line"]}: {token["value"]}')
window = tk.Tk()
window.title('Tokens')
window.geometry('500x250')  
text_area = st.ScrolledText(window, width = 60, height = 15, font = ('Times New Roman',15), foreground = 'white')
text_area.grid(column = 1, row = 1, columnspan=2)
for token in tokens:
    if token['type'] == 'KEYWORD':
        if token['value'] == '\\n':
            text_area.insert(tk.INSERT, '\n')
        else:
            text_area.insert(tk.INSERT, f'{token["value"]} ', )
    elif token['type'] == 'space':
        continue
    else:
        text_area.insert(tk.INSERT, f'{token["type"]} ')
window.mainloop()
