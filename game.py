import time
import tkinter as tk
import random 
import socket
import threading
import json

tiles = []
tile_size = 70
tile_margin = 10
num_rows = 4
num_cols = 4

HOST = "0.0.0.0" # Listen on all interfaces
PORT = 5000 # Use the same port as before
SIZE = 1024 # Define the buffer size


def card_data():
    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine"] # Create a list of words to use as card values
    random.shuffle(words)
    words = words[:8] + words[:8]
    random.shuffle(words)

    return words

def escutar_cliente(conn, addr, data, interface): 
    print(f"Connected by {addr}") 
    conn.send(json.dumps(data).encode())

    while True: 
        data = conn.recv(SIZE) 

        if not data: 
            break 

        data = data.decode() 
        data = json.loads(data) 

        if "flip" in data: 
            tile_index = data["flip"]
            interface.replicate(tile_index)

        response = {"message": "OK"} 
        response = json.dumps(response) 
        response = response.encode() 

        conn.send(response) 

    conn.close() 
    print(f"Disconnected from {addr}") 
    

def escutar_servidor(conn, interface):
    while True:
        data = conn.recv(1024).decode()
        data = json.loads(data)

        if "flip" in data:
            tile_index = data["flip"]
            interface.replicate(tile_index)

def servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((HOST, PORT)) 
    s.listen()

    data = card_data()

    print(f"Escutando em {PORT}")

    conn, addr = s.accept() # Accept a connection from a client
    i = Interface(conn)

    thread = threading.Thread(target=escutar_cliente, args=(conn, addr, data, i)) # Create a new thread to handle the connection
    thread.start() # Start the thread

    i.iniciar('server', data)



def cliente(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
    s.connect((ip.split(':')[0], int(ip.split(':')[1]))) # Connect to the server
    print(f"Connected to {HOST}:{PORT}") # Print a message

    i = Interface(s)
    i.turno = False

    data = s.recv(1024).decode()
    data = json.loads(data)

    threading.Thread(target=escutar_servidor, args=(s, i)).start()
    i.iniciar('cliente', data)


def iniciar(modo, ip='0.0.0.0:5000'):
    if modo == 'server':
        servidor()
    elif modo == 'cliente':
        cliente(ip)

class Interface:
    def __init__(self, conn) -> None:
        
        self.flipped_tiles = []
        self.tiles = []

        self.root = tk.Tk()
        self.turno = True
        self.conn = conn

        self.canvas = tk.Canvas(self.root, width=350, height=350) 
        self.canvas.pack()

        self.tux = None

    def parar(self):
        self.root.destroy()

    def replicate(self, tile_index):
        tile = self.tiles[tile_index]

        if len(self.flipped_tiles) < 2 and not tile.face_up: 
            tile.face_up = True 
            self.flipped_tiles.append(tile)
            tile.draw()

        if len(self.flipped_tiles) == 2:
            self.root.after(800, self.check_tiles)
            self.root.after(800, self.verif_remote)  


    def check_tiles(self):
        if self.flipped_tiles[0].text == self.flipped_tiles[1].text:
            self.canvas.create_rectangle(self.flipped_tiles[0].x, self.flipped_tiles[0].y, self.flipped_tiles[0].x + tile_size, self.flipped_tiles[0].y + tile_size, fill="green") # Draw a green rectangle over the first tile
            self.canvas.create_rectangle(self.flipped_tiles[1].x, self.flipped_tiles[1].y, self.flipped_tiles[1].x + tile_size, self.flipped_tiles[1].y + tile_size, fill="green") # Draw a green rectangle over the second tile

            self.tux = True
        else:
            self.flipped_tiles[0].face_up = False
            self.flipped_tiles[1].face_up = False
                
            self.flipped_tiles[0].draw()
            self.flipped_tiles[1].draw()

            self.tux = False

        self.flipped_tiles = []

    def verif_local(self):
        if self.tux == True:
            self.turno = True
        else:
            self.turno = False

    def verif_remote(self):
        if self.tux == True:
            self.turno = False
        else:
            self.turno = True

    def iniciar(self, mode, data):
        self.root.title("Memory Game")

        # Objeto carta
        class Carta: 
            def __init__(self, x, y, text, canvas): 
                self.x = x
                self.y = y
                self.text = text
                self.face_up = False
                self.canvas = canvas

            def draw(self):
                if self.face_up:
                    self.canvas.create_rectangle(self.x, self.y, self.x + tile_size, self.y + tile_size, fill="white")
                    self.canvas.create_text(self.x + tile_size / 2, self.y + tile_size / 2, text=self.text)
                else:
                    self.canvas.create_rectangle(self.x, self.y, self.x + tile_size, self.y + tile_size, fill="blue")

            def is_under_mouse(self, event):
                if event.x > self.x and event.x < self.x + tile_size:
                    if event.y > self.y and event.y < self.y + tile_size:
                        return True 
                return False

        # Gerar as posições das cartas
        for i in range(num_rows):
            for j in range(num_cols):
                x = j * (tile_size + tile_margin) + tile_margin
                y = i * (tile_size + tile_margin) + tile_margin

                text = data[i * num_cols + j]
                tile = Carta(x, y, text, self.canvas)
                self.tiles.append(tile)

        def mouse_clicked(event):
            if self.turno:
                for i, tile in enumerate(self.tiles):
                    if tile.is_under_mouse(event):
                        if len(self.flipped_tiles) < 2 and not tile.face_up: 
                            tile.face_up = True 
                            self.flipped_tiles.append(tile)
                            tile.draw()
                            message = {"flip": i}
                            self.conn.send(json.dumps(message).encode())
                        if len(self.flipped_tiles) == 2:
                            self.root.after(800, self.check_tiles)
                            self.root.after(800, self.verif_local)



        # Bind the mouse click event to the canvas widget
        self.canvas.bind("<Button-1>", mouse_clicked)

        # Draw all the tiles face down
        for tile in self.tiles:
            tile.draw()

        # Start the main loop of the tkinter window
        self.root.mainloop()
