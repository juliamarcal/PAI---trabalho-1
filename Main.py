import math
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import pandas as pd
import cv2
import numpy as np
from skimage import measure
from skimage.measure import regionprops


class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.caminho_imagem = 'base\\00b1e59ebc3e7be500ef7548207d44e2.png'
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
        botao_segmentar = tk.Button(self.root, text="Segmentar", command=self.crescimento_regiao)
        botao_segmentar.pack()
        
        # Botão de caracterizar
        botao_caracterizar = tk.Button(self.root, text="caracterizar nucleos", command=self.caracterizar_nucleos)
        botao_caracterizar.pack()
        
        # Botão de classificar
        botao_classificar = tk.Button(self.root, text="caracterizar nucleos", command=self.classificar_nucleos)
        botao_classificar.pack()
        

    def abrir_imagem(self):
        # Abrir a caixa de diálogo para selecionar a imagem
        caminho_imagem = filedialog.askopenfilename(
            initialdir="base\\",
            filetypes=[("Imagens", "*.png;*.jpg")]
        )
        img_name = os.path.basename(caminho_imagem)
        
        self.caminho_imagem = f"base\\{img_name}"  # Store the path to the opened image

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

# Segmentação por crescimento de região

    def find_circles(self):
        imagem = cv2.imread(self.caminho_imagem)

        imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY) # Converte a imagem para escala de cinza

        # Aplica um filtro para realçar as características
        imagem_filt = cv2.medianBlur(imagem_gray, 5)

        # Aplica o detector de círculos de Hough
        circles = cv2.HoughCircles(imagem_filt, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                param1=50, param2=30, minRadius=5, maxRadius=30)
        return circles        

    def cres_regiao(self, imagem_gray, seed_x, seed_y):
        _, binarizada = cv2.threshold(imagem_gray, 0, 255, cv2.THRESH_BINARY)

        h, w = binarizada.shape[:2]

        # Convertendo para inteiros
        seed_x, seed_y = int(seed_x), int(seed_y)

        # Máscara para armazenar pixels segmentados
        mask = np.zeros_like(binarizada)

        # Pilha para armazenar pixels a serem verificados
        stack = [(seed_y, seed_x)]

        # Critério de crescimento de região (pode ajustar conforme necessário)
        criterio = 30

        while stack:
            y, x = stack.pop()

            if 0 <= y < h and 0 <= x < w and not mask[y, x] and abs(int(imagem_gray[y, x]) - int(imagem_gray[seed_y, seed_x])) < criterio:
                mask[y, x] = 255

                # Adicionar vizinhos à pilha
                stack.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])

        return mask

    def crescimento_regiao(self):
        sub_images_segmentadas = []
        tamanho_n = int(self.entry_n.get())
        imagem_original = cv2.imread(self.caminho_imagem)
        imagem_gray = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)
        altura, largura = imagem_original.shape[:2]

        # Obter as coordenadas do núcleo do arquivo CSV
        coordenadas_nucleos = self.obter_informacoes_csv()[['nucleus_x', 'nucleus_y','cell_id']]
        if coordenadas_nucleos is not None:
            for centro in coordenadas_nucleos.itertuples(index=False):
                x, y = centro.nucleus_x, centro.nucleus_y
                if 0 <= x < largura and 0 <= y < altura:
                    imagem_segmentada = self.cres_regiao(imagem_gray, x, y)
                    
                    sub_images_segmentadas.append(imagem_segmentada)

                    imagem_colorida = imagem_original.copy()
                    imagem_colorida[imagem_segmentada != 255] = [0, 0, 0]  # Pintar pixels fora da máscara de preto
                    
                    #recortar a imagem
                    imagem_recortada = imagem_colorida[centro[1]-tamanho_n//2:centro[1]+tamanho_n//2, centro[0]-tamanho_n//2:centro[0]+tamanho_n//2]

                    nome_arquivo_segmentado = f'{centro.cell_id}.png'
                    caminho_completo_segmentado = os.path.join("segmentation_images", nome_arquivo_segmentado)
                    if imagem_recortada.size > 0:
                        cv2.imwrite(caminho_completo_segmentado, imagem_recortada)
                else:
                    print(f"Coordenadas fora dos limites: ({x}, {y})")
        else:
            circles = self.find_circles()
            if circles is not None:
                # Converte as coordenadas para inteiros
                circles = np.uint16(np.around(circles))

                centros = []

                for i in circles[0, :]:
                    # Obtém as coordenadas do círculo
                    centro = (i[0], i[1])
                    centros.append(centro)
                    
                    x, y = i[0], i[1]
                    if 0 <= x < largura and 0 <= y < altura:
                        imagem_segmentada = self.cres_regiao(imagem_gray, x, y)
                        
                        sub_images_segmentadas.append(imagem_segmentada)

                        imagem_colorida = imagem_original.copy()
                        imagem_colorida[imagem_segmentada != 255] = [0, 0, 0]  # Pintar pixels fora da máscara de preto
                        
                        #recortar a imagem
                        imagem_recortada = imagem_colorida[centro[1]-tamanho_n//2:centro[1]+tamanho_n//2, centro[0]-tamanho_n//2:centro[0]+tamanho_n//2]

                        nome_arquivo_segmentado = f'{centro.cell_id}.png'
                        caminho_completo_segmentado = os.path.join("segmentation_images", nome_arquivo_segmentado)
                        if imagem_recortada is not None:
                            cv2.imwrite(caminho_completo_segmentado, imagem_recortada)
                    else:
                        print(f"Coordenadas fora dos limites: ({x}, {y})")
                self.comparar_centros(centros)
        self.caracterizar_nucleos()
        return sub_images_segmentadas

# Caracterização
    def caracterizar_nucleos(self):
        resultados_df = pd.DataFrame(columns=['area', 'perimetro', 'circunferencia','compacidade', 'excentricidade'])
        sub_images = os.listdir(".\segmentation_images")

        for sub_image in sub_images:
            image = Image.open(".\\segmentation_images\\"+sub_image)
            imagem_cinza = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
            _,imagem_binaria = cv2.threshold(imagem_cinza, 128,255, cv2.THRESH_BINARY)
            caracterizacao = measure.label(imagem_binaria,background = 0)

            for regiao in regionprops(caracterizacao):
                area = regiao.area
                perimetro = regiao.perimeter
                if perimetro != 0:
                    circunferencia = (perimetro ** 2)/(4 * np.pi * area) 
                else:
                    circunferencia = 0
                compacidade = (4 * np.pi * area) / (perimetro ** 2)
                
                # Calcular momentos da região
                momentos = regiao.moments_central
            
                # Calcular semi-eixos
                a = np.sqrt(2 * (momentos[2, 0] + momentos[0, 2] + np.sqrt((momentos[2, 0] - momentos[0, 2])**2 + 4 * momentos[1, 1]**2 - 2 * (momentos[2, 0] + momentos[0, 2]) * (momentos[2, 0] + momentos[0, 2]))))
                b = np.sqrt(2 * (momentos[2, 0] + momentos[0, 2] - np.sqrt((momentos[2, 0] - momentos[0, 2])**2 + 4 * momentos[1, 1]**2 - 2 * (momentos[2, 0] + momentos[0, 2]) * (momentos[2, 0] + momentos[0, 2]))))

                # Calcular excentricidade
                excentricidade = np.sqrt(1 - (b**2) / (a**2))

                resultados_df.loc[len(resultados_df)] = [area, perimetro, circunferencia,compacidade,excentricidade]
        print(resultados_df.shape)
        resultados_df.to_csv('resultados_caracterizacao.csv', index=False)
        self.exibir_tabela('resultados_caracterizacao.csv')

# Classificação
    def classificar_nucleos(self):
        imagens_segmentadas = '.\\segmentation_images'
        dados_csv_path = 'classifications.csv'
        dados_csv = pd.read_csv(dados_csv_path)

        for indice, linha in dados_csv.iterrows():
            cell_id = str(linha['cell_id'])
            caminho_image = None

            # Procura a imagem correspondente ao cell_id
            for arquivo in os.listdir(imagens_segmentadas):
                if arquivo == f"{cell_id}.png":
                    caminho_image = os.path.join(imagens_segmentadas, arquivo)
                    break

            if caminho_image is not None and os.path.exists(caminho_image):
                subpasta = os.path.join(imagens_segmentadas, str(linha['bethesda_system']))
                
                if not os.path.exists(subpasta):
                    os.makedirs(subpasta)

                novo_caminho = os.path.join(subpasta, f"{cell_id}.png")
                shutil.move(caminho_image, novo_caminho)

# utils
    def obter_informacoes_csv(self):
        img_name = os.path.basename(self.caminho_imagem)
        
        # Carregue o arquivo CSV em um DataFrame
        df = pd.read_csv('classifications.csv')

        # Filtrar o DataFrame com base na condição do image_filename
        resultados_filtrados = df[df['image_filename'] == img_name]
        
        return resultados_filtrados
      
    def comparar_centros(self, centros, output_file='distancias.txt'):
        coordenadas_nucleos_csv = self.obter_informacoes_csv()[['nucleus_x', 'nucleus_y']]
        distancias = []

        for centro in centros:
            distancia_minima = float('inf')
            for _, coordenada in coordenadas_nucleos_csv.iterrows():
                distancia = math.sqrt((centro[0] - coordenada['nucleus_x'])**2 + (centro[1] - coordenada['nucleus_y'])**2)
                if distancia < distancia_minima:
                    distancia_minima = distancia

            distancias.append(distancia_minima)

        # Salvar distâncias em um arquivo TXT
        with open(output_file, 'w') as file:
            for distancia in distancias:
                file.write(f'{distancia}\n')

        return distancias
    
    def exibir_tabela(self,planilha):
        dados = pd.read_csv(planilha)
        root = tk.Tk()
        root.title("Tabela Caracterização")

        tree = ttk.Treeview(root)

        # Configurar as colunas
        colunas = list(dados.columns)
        tree["columns"] = colunas
        for coluna in colunas:
            tree.column(coluna, anchor="center", width=100)
            tree.heading(coluna, text=coluna, anchor="center")

        # Adicionar os dados à árvore
        for indice, linha in dados.iterrows():
            tree.insert("", indice, values=tuple(linha))

        # Adicionar a árvore a uma barra de rolagem
        scroll_y = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        tree.pack()

        root.mainloop()

# main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
