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
        self.zoom_factor = 1.0
        self.image_id = None

        # Adicionar evento de rolagem do mouse para zoom
        self.canvas.bind("<MouseWheel>", self.zoom_mouse)

        # Botão para zoom in
        btn_zoom_in = tk.Button(self.root, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.pack()

        # Botão para zoom out
        btn_zoom_out = tk.Button(self.root, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.pack()

    def abrir_imagem(self):
        # Abrir a caixa de diálogo para selecionar a imagem
        caminho_imagem = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg")])

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
        self.zoom_factor *= 1.2
        self.atualizar_zoom()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.atualizar_zoom()

    def zoom_mouse(self, event):
        # Evento de rolagem do mouse para zoom
        if event.delta > 0:
            self.zoom_factor *= 1.2
        else:
            self.zoom_factor /= 1.2
        self.atualizar_zoom(event.x, event.y)

    def atualizar_zoom(self, x=None, y=None):
        # Atualizar o zoom considerando a posição do mouse
        self.canvas.scale(self.image_id, None, None, self.zoom_factor, self.zoom_factor)

    
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
