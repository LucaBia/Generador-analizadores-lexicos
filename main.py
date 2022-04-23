import tkinter as tk
from tkinter import filedialog


def UploadAction(event=None):
    filename = filedialog.askopenfilename()
    print('Archivo seleccionado:', filename)

window = tk.Tk()
window.title("Analizador Lexico")
window.geometry('400x300')
# greeting = tk.Label(text="Hello, Tkinter")
# greeting.pack()
button = tk.Button(window, text='Open', command=UploadAction)
button.pack()
window.mainloop()