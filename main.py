# Import tkinter module
import tkinter as tk
from game import iniciar

def iniciar_interface(modo, ip):
    root.destroy()
    iniciar(modo, ip)

root = tk.Tk()

label = tk.Label(root, text="Servidor ou cliente?")
label.pack()

choice = tk.StringVar()

server = tk.Radiobutton(root, text="Servidor", value="server", variable=choice)
client = tk.Radiobutton(root, text="Cliente", value="client", variable=choice)

server.pack()
client.pack()

def confirmar():
    c = choice.get()

    if c == "client":
        texto_ip.pack()
        campo_ip.pack()
        confirm2.pack()

    elif c == "server":
        texto_ip.pack_forget()
        campo_ip.pack_forget()
        iniciar_interface('server', None)


texto_ip = tk.Label(root, text="Ip do servidor:")
campo_ip = tk.Entry(root)
campo_ip.insert(0, '127.0.0.1:5000')

confirm2 = tk.Button(root, text="Confirmar", command=lambda: iniciar_interface('cliente', campo_ip.get()))

botao = tk.Button(root, text="Confirmar", command=confirmar)
botao.pack()

root.mainloop()