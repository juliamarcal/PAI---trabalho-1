import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from skimage import color, filters
import cv2
import numpy as np

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

def classificar_nucleos(self):
    return

def caracterizar_nucleos(self):
    return

