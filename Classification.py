import cv2
import numpy as np
from PIL import Image
import tkinter as tk
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

class Classification:
    def extrair_descritores_forma(imagem):

        imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        _, imagem_binaria = cv2.threshold(imagem_cinza, 128, 255, cv2.THRESH_BINARY)

        contornos, _ = cv2.findContours(imagem_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        maior_contorno = max(contornos, key=cv2.contourArea)

        area = cv2.contourArea(maior_contorno)
        perimetro = cv2.arcLength(maior_contorno, True)
        circularidade = (4 * np.pi * area) / (perimetro ** 2)

        descritores_forma =  {
            'area': area,
            'perimetro': perimetro,
            'circularidade': circularidade,
        
        }

        self.nucleos_caracterizados = descritores_forma

        for chave, valor in descritores_forma.items():
            tk.Label(self.root, text=f'{chave}: {valor}').pack()

    def classificar_nucleos(self,descritores_forma):

        caminho_arquivo_csv = 'classifications.csv'
        dados = pd.read_csv(caminho_arquivo_csv)

        X = dados[['nucleus_x', 'nucleus_y']]
        y = dados['bethesda_system'] 

        X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

        modelo = RandomForestClassifier(random_state=42)
        modelo.fit(X_treino, y_treino)

        previsoes = modelo.predict(X_teste)

        acuracia = accuracy_score(y_teste, previsoes)
        print(f'Acurácia do modelo: {acuracia}')

        if self.nucleos_caracterizados:
            modelo = self.classificar_nucleos_dummy(self.nucleos_caracterizados)

            tk.Label(self.root, text=f'Resultado da Classificação: {modelo}').pack()

        if descritores_forma['area'] > 50 and descritores_forma['circularidade'] > 0.7:
            return "Núcleo Benigno"
        else:
            return "Núcleo Maligno"
        
    caminho_imagem = 'base\\00b1e59ebc3e7be500ef7548207d44e2.png'

    imagem = Image.open(caminho_imagem)

    imagem = cv2.imread(caminho_imagem)

    descritores_forma = extrair_descritores_forma(imagem)

    print("Dados: ",descritores_forma)

    classifica_forma = classificar_nucleos(descritores_forma)

    print("Dados: ",classifica_forma)