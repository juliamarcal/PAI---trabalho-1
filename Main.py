import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Processamento de Imagens")

        # Criar o menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Abrir Imagem", command=self.abrir_imagem)
        menu_arquivo.add_command(label="Sair", command=self.root.destroy)

        # Frame para exibir a imagem
        self.frame_imagem = tk.Frame(self.root)
        self.frame_imagem.pack(pady=10)

        # Botão para segmentar núcleos
        btn_segmentar = tk.Button(self.root, text="Segmentar Núcleos", command=self.segmentar_nucleos)
        btn_segmentar.pack()

        # Botão para caracterizar núcleos
        btn_caracterizar = tk.Button(self.root, text="Caracterizar Núcleos", command=self.caracterizar_nucleos)
        btn_caracterizar.pack()

        # Botão para classificar núcleos
        btn_classificar = tk.Button(self.root, text="Classificar Núcleos", command=self.classificar_nucleos)
        btn_classificar.pack()

    def abrir_imagem(self):
        # Abrir a caixa de diálogo para selecionar a imagem
        caminho_imagem = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg")])

        # Exibir a imagem no frame
        imagem = Image.open(caminho_imagem)
        imagem = ImageTk.PhotoImage(imagem)
        label_imagem = tk.Label(self.frame_imagem, image=imagem)
        label_imagem.imagem = imagem  # Manter uma referência para evitar a coleta de lixo
        label_imagem.pack()

    def segmentar_nucleos(self):
        # Implementar a lógica de segmentação de núcleos aqui
        pass

    def caracterizar_nucleos(self):
        # Implementar a lógica de caracterização de núcleos aqui
        pass

    def classificar_nucleos(self):
        # Implementar a lógica de classificação de núcleos aqui
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
