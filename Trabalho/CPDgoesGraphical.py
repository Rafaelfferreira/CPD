'''

    IMPORTS NECESSÁRIOS

'''



from tkinter import *
from tkinter import ttk   # para a combobox
import pandas as pd
import xlrd
import pickle #modulo usado para serializar dados para o arquivo binario
import os
import time
import copy
from unicodedata import normalize
from TRIE import *
from Queries import *


'''''''''''''''

    Fazendo a leitura dos arquivos

'''''''''''''''

#Faz a leitura do arquivo de registros
with (open('database.bin', 'rb')) as openfile:
    database = pickle.load(openfile)

#Leitura do arquivo de indices de anos
with (open('indices.bin', 'rb')) as openfile:
    indices = pickle.load(openfile)

#Leitura do arquivo com a arvore TRIE de titulos de musicas
with open('trieMusicas.bin','rb') as openfile:
    trieMusicas = pickle.load(openfile)

#Leitura do arquivo com a arvore TRIE de nomes de artistas
with open('trieArtistas.bin','rb') as openfile:
    trieArtistas = pickle.load(openfile)

with (open('topArtistas.bin', 'rb')) as openfile:
    topArtistas = pickle.load(openfile)

with (open('topMusicas.bin', 'rb')) as openfile:
    topMusicas = pickle.load(openfile)








# DEFINE DAS QUERIES:
QUERIES = [

    "Os n artistas mais relevantes",
    "Os 10 artistas mais relevantes do ano"

]













'''

    Definições da GUI

'''

welcomeMessage = "Bem-vindo ao Billboard 100! \n\nPara efetuar buscas: \n"
welcomeMessage = welcomeMessage + "1. Selecione o tipo da busca\n2. Entre com a entrada descrita abaixo\n3. Clike no botão de busca"
welcomeMessage = welcomeMessage + "\n\nEntradas:\n1. Os n artistas mais relevantes: digite a quantidade (número) de artistas que se deseja listar."
welcomeMessage = welcomeMessage + "\n2. Os 10 artistas mais relevantes do ano: digite o ano (número) que se deseja procurar."


# Popup de erro, recebe uma string (mensagem de erro) e exibe em uma nova janela esta mensagem
def popupErro(msg):
    popup = Tk()
    popup.resizable(width=False, height=False)
    popup.iconbitmap('b_icon.ico')
    popup.wm_title("Erro!")
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Ok", command = popup.destroy)
    B1.pack()
    popup.mainloop()




# função chamada quando o botão BUSCA é pressionado
def busca():
    string = input.get()   # pega o texto da caixa de texto para realizar a busca
    option = selectDrop.get()   # pega o valor selecionado no combobox

# Query dos n artistas mais relevantes escolhida:
    if option == QUERIES[0]:

        try:   # tenta converter a string de entrada para número inteiro
            n = int(string)
        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        resultado = topArtistasQuery(topArtistas, n, False)

# Query dos 10 artistas mais relevantes de determinado ano:
    elif option == QUERIES[1]:

        try:   # tenta converter a string de entrada para número inteiro
            ano = int(string)

            # testa se é um ano válido
######################   IMPLEMENTAR   #########################################################################

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        resultado = relevanciaArtistaAno(database, indices, ano, 10, True)




    output.config(state=NORMAL)   # habilita edição da text box
    output.delete(0.0, END)   # apaga a label de saída antes de printar novos resultados
    output.insert(END, resultado)   # insere resultado
    output.config(state=DISABLED)   # desabilita edição da text box novamente

# main
window = Tk()

# seta um título na janela
window.title("Billboard 100")
# seta tamanho da janela
window.geometry("254x500")
# seta cor de fundo da janela
window.configure(background="white")
# bloqueia redimensionamento da janela
window.resizable(width=False, height=False)
# define icone da janela
window.iconbitmap('b_icon.ico')

# logo da billboard
billboardLogo = PhotoImage(file="billboard.gif")
# o columnspan do grid define que a imagem vai ocupar duas colunas
Label (window, image=billboardLogo, bg="white") .grid(row=0, column=0, columnspan=2, sticky=W)

# bg: backgroung | fg: cor da fonte do texto | font: none pra default, 12 pro tamanho, bold para negrito
Label (window, text="Escolha o tipo de busca:", bg="white", fg="black", font="none 12 bold") .grid(row=1, column=0, sticky=W)

# combobox seletor de qual tipo de busca pretende-se fazer:
selectDrop = ttk.Combobox(window, state="readonly", width=35)
selectDrop.grid(row=2, column=0, columnspan=2, sticky=W, padx=4)
# valores do combobox
selectDrop['values']= (
    QUERIES[0],
    QUERIES[1],
    "query 3"
)
# valor default
selectDrop.current(newindex=0)


# texto de busca (entrada)
input = Entry(window, width=22, font="none 11", bg="white")
# o padx no grid determina um espaçamento
input.grid(row=3, column=0, sticky=W, padx=4)   # grid definido aqui embaixo para não bugar o método get()

# botão de busca
Button(window, text="BUSCA", width=5, command=busca) .grid(row=3, column=0, padx=200, sticky=W)

# cria textbox de output (onde os resultados vão ser printados)
output = Text (window, width=28, height=15, wrap=WORD, background="white")
output.grid(row=4, column=0, columnspan=2, padx=4, pady=15, sticky=W)
output.insert(END, welcomeMessage)
output.config(state=DISABLED)   # não permite mexer na text box (tem que habilitar para inserir texto mesmo com .insert())
# scrollbar  para textbox:
scrollb = Scrollbar(window, command=output.yview)
scrollb.grid(row=4, column=0, padx=235, ipady=97)   # sendo ipady o tamanho da scrollbar
output['yscrollcommand'] = scrollb.set


window.mainloop()
