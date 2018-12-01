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
    "Os n artistas mais relevantes do ano"

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
    string = input1.get()   # pega o texto da caixa de texto para realizar a busca
    option = selectDrop.get()   # pega o valor selecionado no combobox
    reverse = varCheckButton.get()

# Query dos n artistas mais relevantes escolhida:
    if option == QUERIES[0]:

        try:   # tenta converter a string de entrada para número inteiro
            n = int(string)
        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        resultado = topArtistasQuery(topArtistas, n, reverse)

# Query dos n artistas mais relevantes de determinado ano:
    elif option == QUERIES[1]:

        try:   # tenta converter a string de entrada para número inteiro
            n = int(string)

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        # repete o mesmo processo para o input do ano
        ano = input2.get()

        try:   # tenta converter a string de entrada para número inteiro
            ano = int(ano)

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return


        resultado = relevanciaArtistaAno(database, indices, ano, n, reverse)




    output.config(state=NORMAL)   # habilita edição da text box
    output.delete(0.0, END)   # apaga a label de saída antes de printar novos resultados
    output.insert(END, resultado)   # insere resultado
    output.config(state=DISABLED)   # desabilita edição da text box novamente



# função chamada toda vez que a a seleção da combobox mudar
# habilita/desabilita caixas de entrada e muda mensagem que pede input para cada caixa
def comboboxChanged(event):

    # pega qual busca foi selecionada
    selection = selectDrop.get()

    # query: "Os n artistas mais relevantes"
    if selection == QUERIES[0]:

        # só a primeira caixa habilitada (sempre, não precisa mudar)
        input2.config(state=DISABLED)
        input3.config(state=DISABLED)
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Número de artistas:')
        msgInput2.config(text='')
        msgInput3.config(text='')
        msgInput4.config(text='')


    # query: "Os n artistas mais relevantes do ano"
    if selection == QUERIES[1]:

        # primeira e segunda caixas habilitadas
        input2.config(state=NORMAL)
        input3.config(state=DISABLED)
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Número de artistas:')
        msgInput2.config(text='Ano de interesse:')
        msgInput3.config(text='')
        msgInput4.config(text='')







# main
window = Tk()

# seta um título na janela
window.title("Billboard 100")
# seta tamanho da janela
window.geometry("505x530")
# seta cor de fundo da janela
window.configure(background="white")
# bloqueia redimensionamento da janela
window.resizable(width=False, height=False)
# define icone da janela
window.iconbitmap('b_icon.ico')

# logo da billboard
billboardLogo = PhotoImage(file="Billboard_original_500.gif")
# o columnspan do grid define que a imagem vai ocupar duas colunas
Label (window, image=billboardLogo, bg="white") .grid(row=0, column=0, columnspan=2, sticky=W)

# bg: backgroung | fg: cor da fonte do texto | font: none pra default, 12 pro tamanho, bold para negrito
Label (window, text="Escolha o tipo de busca:", bg="white", fg="black", font="none 12 bold") .grid(row=1, column=0, sticky=W, pady=(20,0))

# combobox seletor de qual tipo de busca pretende-se fazer:
selectDrop = ttk.Combobox(window, state="readonly", width=57)
selectDrop.grid(row=2, column=0, columnspan=2, sticky=W, padx=4, pady=(0,10))
# valores do combobox
selectDrop['values']= (
    QUERIES[0],
    QUERIES[1]
)
# valor default
selectDrop.current(newindex=0)
selectDrop.bind("<<ComboboxSelected>>", comboboxChanged)

# botão de busca
Button(window, text="BUSCA", width=5, command=busca) .grid(row=2, column=0, columnspan=2, padx=(380,0), pady=(0,10), sticky=W)

# botão de check para habilitar/desabilitar busca reversa
varCheckButton = IntVar()
checkButton = Checkbutton(window, text="Reversa", variable=varCheckButton, bg="white")
checkButton.grid(row=2, column=0, columnspan=2, padx=(430,0), pady=(0,10), sticky=W)


'''

    Parte da GUI com as 4 entryboxes e 4 labels indicando qual deve ser o input

'''


# mensagem pedindo primeiro input
msgInput1 = Label (window, text="Número de artistas:", bg="white", fg="black", font="none 10")
msgInput1.grid(row=3, column=0, sticky=W, padx=4)
# texto de entrada 1
input1 = Entry(window, font="none 11", bg="white")
# o padx no grid determina um espaçamento
input1.grid(row=4, column=0, sticky=EW, padx=4)   # grid definido aqui embaixo para não bugar o método get()


# mensagem pedindo segundo input
msgInput2 = Label (window, text="", bg="white", fg="black", font="none 10")
msgInput2.grid(row=3, column=1, sticky=W, padx=4)
# texto de entrada 2
input2 = Entry(window, font="none 11", bg="white")
input2.grid(row=4, column=1, sticky=EW, padx=4)


# mensagem pedindo terceiro input
msgInput3 = Label (window, text="", bg="white", fg="black", font="none 10")
msgInput3.grid(row=5, column=0, sticky=W, padx=4)
# texto de entrada 3
input3 = Entry(window, font="none 11", bg="white")
input3.grid(row=6, column=0, sticky=EW, padx=4)


# mensagem pedindo quarto input
msgInput4 = Label (window, text="", bg="white", fg="black", font="none 10")
msgInput4.grid(row=5, column=1, sticky=W, padx=4)
# texto de entrada 3
input4 = Entry(window, font="none 11", bg="white")
input4.grid(row=6, column=1, sticky=EW, padx=4)

# desabilita edição das caixas que não serão utilizadas
input2.config(state=DISABLED)
input3.config(state=DISABLED)
input4.config(state=DISABLED)



'''

    Parte da GUI com a textbox de saída

'''


# cria textbox de output (onde os resultados vão ser printados)
output = Text (window, width=59, height=12, wrap=WORD)
output.grid(row=7, column=0, columnspan=2, padx=4, pady=15, sticky=W)
output.insert(END, welcomeMessage)
output.config(state=DISABLED)   # não permite mexer na text box (tem que habilitar para inserir texto mesmo com .insert())
# scrollbar  para textbox:
scrollb = Scrollbar(window, command=output.yview)
scrollb.grid(row=7, column=0, columnspan=2, padx=(480,0), pady=15, ipady=72)   # sendo ipady o tamanho da scrollbar
output['yscrollcommand'] = scrollb.set


window.mainloop()
