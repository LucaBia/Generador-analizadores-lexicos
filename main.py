import tkinter as tk
from tkinter import CENTER, filedialog
from tkinter import scrolledtext as st


def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("Text files", "*.txt*"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo1_ = "./" + filename_splited
    label_file_explorer.configure(text=archivo1_)
    archivo1.set(archivo1_)

def browseFiles2():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("Text files", "*.txt*"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo2_ = "./" + filename_splited
    label_file_explorer2.configure(text=archivo2_)
    archivo2.set(archivo2_)


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
  
label_file_explorer.grid(column = 1, row = 1)  
button_explore.grid(column = 2, row = 1)
label_file_explorer2.grid(column = 1, row = 2)  
button_explore2.grid(column = 2, row = 2)
text_area.grid(column = 1, row = 3, columnspan=2)
# text_area.configure(state ='disabled')
creador.grid(column = 1,row = 4, columnspan=2)

text_area.insert(tk.INSERT,"UNAAAAAAAA")
text_area.insert(tk.INSERT,"\n")
text_area.insert(tk.INSERT,"DOSSSSS")

# Espera que se suban archivos para continuar
button_explore.wait_variable(archivo1)
button_explore2.wait_variable(archivo2)

print("Archivo1: ", archivo1.get())
print("Archivo2: ", archivo2.get())


  
window.mainloop()