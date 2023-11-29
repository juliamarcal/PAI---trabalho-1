import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import pandas as pd
from skimage import color, filters
import cv2
import numpy as np
from skimage.segmentation import flood_fill
# import Classification
# from Segmentation import perform_segmentation

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
        self.canvas.bind("<MouseWheel>", self.zoom_mouse) # zoom com mouse

        # Slider zoom
        self.zoom_slider = tk.Scale(self.root, from_=0.6, to=5, orient=tk.HORIZONTAL, resolution=0.1, label="Zoom", command=self.update_zoom_from_slider)
        self.zoom_slider.set(0.6)
        self.zoom_slider.pack()
        
        # Campo de texto para o valor de N
        self.label_n = tk.Label(self.root, text="Valor de N:")
        self.label_n.pack()
        self.entry_n = tk.Entry(self.root)
        self.entry_n.insert(0, "100")  # Valor padrão
        self.entry_n.pack()

        # Botão de segmentação
        botao_segmentar = tk.Button(self.root, text="Segmentar", command=self.segmentar_nucleos)
        botao_segmentar.pack()
        
        # Botão de segmentação por crescimento de região
        botao_segmentar_crescimento = tk.Button(self.root, text="Segmentar - crescimento de reg", command=self.crescimento_regiao)
        botao_segmentar_crescimento.pack()
        
        # Botão de caracterizar
        botao_caracterizar = tk.Button(self.root, text="caracterizar nucleos", command=self.caracterizar_nucleos)
        botao_caracterizar.pack()
        
        # Botão de classificação
        botao_classificar = tk.Button(self.root, text="classificar nucleos", command=self.classificar_nucleos)
        botao_classificar.pack()

    def abrir_imagem(self):
        # Abrir a caixa de diálogo para selecionar a imagem
        # caminho_imagem = filedialog.askopenfilename(
        #     initialdir="/path/to/initial/directory",
        #     filetypes=[("Imagens", "*.png;*.jpg")]
        # )
        
        caminho_imagem = "base\\00b1e59ebc3e7be500ef7548207d44e2.png"

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

# funções para zoom
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


# Segmentação - Transformada de Hough para círculos (HoughCircles)
    def segmentar_nucleos(self):
        imagem = cv2.imread(self.caminho_imagem)

        imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY) # Converte a imagem para escala de cinza

        # Aplica um filtro para realçar as características
        imagem_filt = cv2.medianBlur(imagem_gray, 5)

        # Aplica o detector de círculos de Hough
        circles = cv2.HoughCircles(imagem_filt, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                param1=50, param2=30, minRadius=5, maxRadius=30)

        if circles is not None:
            # Converte as coordenadas para inteiros
            circles = np.uint16(np.around(circles))

            # Lista para armazenar as sub-imagens
            sub_images = []

            for i in circles[0, :]:
                # Obtém as coordenadas do círculo
                centro = (i[0], i[1])

                # Recorta uma região 100x100 ao redor do centro
                tamanho_n = int(self.entry_n.get())
                sub_image = imagem[centro[1]-tamanho_n//2:centro[1]+tamanho_n//2, centro[0]-tamanho_n//2:centro[0]+tamanho_n//2]

                # Armazena a sub-imagem
                sub_images.append(sub_image)

                # Salva a sub-imagem em um arquivo
                nome_arquivo = f'nucleo_{centro[0]}_{centro[1]}.png'
                caminho_completo = os.path.join("segmentation_images", nome_arquivo)
                cv2.imwrite(caminho_completo, sub_image)

            return sub_images
        else:
            print("Nenhum núcleo detectado.")
            return None

# Segmentação por crescimento de região
    def cres_regiao(self, imagem_gray, seed_x, seed_y):
        _, binarizada = cv2.threshold(imagem_gray, 0, 255, cv2.THRESH_BINARY)
        imagem_segmentada = flood_fill(binarizada, (seed_y, seed_x), 255)
        return imagem_segmentada

    def crescimento_regiao(self):
        # imagem = cv2.imread(self.caminho_imagem)

        # Selecionar diretamente o arquivo "classifications.csv"
        caminho_csv = "classifications.csv"
        dados = pd.read_csv(caminho_csv)

        # Exibir a imagem no canvas
        imagem = cv2.imread(self.caminho_imagem)
        imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        # Obter as coordenadas do núcleo do arquivo CSV
        coordenadas_nucleos = [(int(x), int(y)) for x, y in zip(dados['nucleus_x'], dados['nucleus_y'])]

        # Lista para armazenar as sub-imagens segmentadas
        sub_images_segmentadas = []

        for centro in coordenadas_nucleos:
            imagem_segmentada = self.cres_regiao(imagem_gray, centro[0], centro[1])
            sub_images_segmentadas.append(imagem_segmentada)

            nome_arquivo_segmentado = f'nucleo_{centro[0]}_{centro[1]}_segmentado.png'
            caminho_completo_segmentado = os.path.join("segmentation_images", nome_arquivo_segmentado)
            cv2.imwrite(caminho_completo_segmentado, imagem_segmentada)

        return sub_images_segmentadas

# Classificação
    def classificar_nucleos(self):
        return

# Caracterização
    def caracterizar_nucleos(self):
        return
    
# main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
