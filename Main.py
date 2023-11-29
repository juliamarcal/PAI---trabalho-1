import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Processamento de Imagens")

        # Tamanho fixo para o Canvas com padding
        self.canvas_width = 1000
        self.canvas_height = 800
        self.padding = 20

        # Criar o menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Abrir Imagem", command=self.abrir_imagem)
        menu_arquivo.add_command(label="Sair", command=self.root.destroy)

        # Canvas para exibir a imagem com barras de rolagem
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adicionar barras de rolagem
        scrollbar_vertical = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_horizontal = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

        # Inicializar variáveis de zoom
        self.zoom_factor = 0.6
        self.image_id = None
        self.caminho_imagem = None  # Store the path to the opened image

        # Adicionar evento de rolagem do mouse para zoom
        self.canvas.bind("<MouseWheel>", self.zoom_mouse)

        # Slider for zoom control
        self.zoom_slider = tk.Scale(self.root, from_=0.6, to=5, orient=tk.HORIZONTAL, resolution=0.1, label="Zoom", command=self.update_zoom_from_slider)
        self.zoom_slider.set(0.6)
        self.zoom_slider.pack()

    def abrir_imagem(self):
        # Abrir a caixa de diálogo para selecionar a imagem
        caminho_imagem = filedialog.askopenfilename(
            initialdir="/path/to/initial/directory",
            filetypes=[("Imagens", "*.png;*.jpg")]
        )

        self.caminho_imagem = caminho_imagem  # Store the path to the opened image

        # Exibir a imagem no canvas
        imagem = Image.open(caminho_imagem)

        # Redimensionar a imagem
        tamanho_redimensionado = (int(imagem.width * 0.6), int(imagem.height * 0.6))
        imagem = imagem.resize(tamanho_redimensionado, Image.ANTIALIAS)

        imagem = ImageTk.PhotoImage(imagem)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Calcular as coordenadas para centralizar a imagem no Canvas com padding
        x = (self.canvas_width - imagem.width()) / 2
        y = (self.canvas_height - imagem.height()) / 2

        self.image_id = self.canvas.create_image(x, y, anchor="nw", image=imagem)
        self.canvas.itemconfig(self.image_id, image=imagem)  # Atualizar a imagem
        self.canvas.image = imagem  # Manter uma referência para evitar a coleta de lixo

    def zoom_in(self):
        current_zoom = self.zoom_slider.get()
        new_zoom = min(5.0, current_zoom * 1.2)
        self.zoom_slider.set(new_zoom)
        self.atualizar_zoom()

    def zoom_out(self):
        current_zoom = self.zoom_slider.get()
        new_zoom = max(0.6, current_zoom / 1.2)
        self.zoom_slider.set(new_zoom)
        self.atualizar_zoom()

    def zoom_mouse(self, event):
        # Evento de rolagem do mouse para zoom
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def atualizar_zoom(self, x=None, y=None):
        zoom_value = self.zoom_slider.get()
        imagem = Image.open(self.caminho_imagem)
        tamanho_redimensionado = (int(imagem.width * zoom_value), int(imagem.height * zoom_value))
        imagem_resized = imagem.resize(tamanho_redimensionado, Image.ANTIALIAS)
        imagem_tk = ImageTk.PhotoImage(imagem_resized)

        # Update canvas with the new resized image
        self.canvas.itemconfig(self.image_id, image=imagem_tk)
        self.canvas.image = imagem_tk  # Keep a reference to avoid garbage collection

    def update_zoom_from_slider(self, value):
        self.atualizar_zoom()

    
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
