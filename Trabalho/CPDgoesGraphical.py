'''

    IMPORTS NECESSÁRIOS

'''



from tkinter import *
from tkinter import ttk   # para a combobox
from tkinter import filedialog # para procurar arquivo
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
    "Os n artistas mais relevantes do ano",
    "Busca de músicas mais relevantes",
    "Compara artistas e quantas semanas o mais relevante se manteve",
    "Compara músicas e quantas semanas a mais relevante se manteve",
    "Sugestão de artistas",
    "Sugestão de músicas",
    "Lista de músicas de um dado artista"

]





'''

    Definição das funções de inserção de novos dados e novo registro (único)

'''

def adicionaAno(arquivo):

    df = pd.read_excel(arquivo) #Le o arquivo de excel para a variavel Dataframe


    contador = {}
    #Salva os registros do ano atual
    for i in range(len(df)):
        ano = df['WeekID'][0].split('-')
        ano = ano[0]
        if(df['SongID'][i] in contador): #testa se a musica ja esta no dicionario (ja foi computada)
            contador[df['SongID'][i]]['Pontos'] += (101 - df['Week Position'][i])
        else: #cai aqui se ainda nao foi computada
            contador[df['SongID'][i]] = {}
            contador[df['SongID'][i]]['Artista'] = df['Performer'][i]
            contador[df['SongID'][i]]['Titulo'] = df['Song'][i]
            contador[df['SongID'][i]]['Ano'] = ano
            contador[df['SongID'][i]]['Pontos'] = (101 - df['Week Position'][i])
            #A medida 'Peak' nao eh a posicao exata que ela atingiu mas os "pontos maximos" ganhos em uma semana (de 1 a 100)
            contador[df['SongID'][i]]['Peak'] = (101 - df['Peak Position'][i]) #salva qual foi a maior posicao alcançada pela musica (usada para criterios de desempate)
            contador[df['SongID'][i]]['Semanas'] = df['Weeks on Chart'][i] #Terceiro criterio de desempate

    #Faz o sort do ano atual
    items = sorted(contador.items(), key = lambda tup: (tup[1]["Pontos"], tup[1]["Peak"], tup[1]["Semanas"]), reverse=True)

    #armazena as primeiras 200 entradas em um dicionário mais organizado
    top = [dict() for x in range(200)] #cria uma lista de 200 dicionarios
    for i in range(len(top)):

        for y in items[i][1]:
            top[i][y] = items[i][1][y]

        # Adiciona no dicionário de todos os artistas (ou soma os pontos) para cianção do arquivo topArtistas.bin
        artistaIterado = retiraFeaturing(str(top[i]['Artista']))   # retira o featuring caso tenha

        indArtista = -1 #flag que salva o indice do artista iterado, se for -1 o artista nao esta na lista
        indice = 0 #indice que esta procurando o artista
        for x in topArtistas: #percorre o arquivo topArtistas procurando pelo artista
            if x[0] == artistaIterado:
                indArtista = indice
            indice += 1

        if(indArtista != -1): #Se o artista ja esta na lista
            topArtistas[indArtista] = (artistaIterado, topArtistas[indArtista][1] + top[i]['Pontos'])
        else: #cria um novo artista
            topArtistas.append((artistaIterado, top[i]['Pontos'])) #da um append com a tupla 'nome artista' + 'pontos'

    #Concatena o dicionario no arquivo teste.bin
    filename = 'database.bin'
    topBytes = []


    if os.path.exists(filename): #confere se o arquivo existe
        with open(filename,'rb') as openfile:  #with automaticamente da um close() no final
            topBytes = pickle.load(openfile) #carrega o que ja esta salvo no arquivo

    indIni = len(topBytes) #Salva o primeiro bit dos dados novos que foram inseridos

    newData = top #Aqui vem a nova data que deve ser concatenada

    topBytes = topBytes + newData #concatena o que ja tinha no arquivo binario com a nova data

    with (open(filename, 'wb+')) as openfile: #abre o arquivo no modo de leitura binaria 'wb' como openfile
        pickle.dump(topBytes, openfile)

    #-----------------------------------------------------------------------------
    #Cria o arquivo de indice para consultas
    #-----------------------------------------------------------------------------
    filename = 'indices.bin'
    fileBytes = []

    if os.path.exists(filename): #confere se o arquivo existe
        with open(filename,'rb') as openfile:  #with automaticamente da um close() no final
            fileBytes = pickle.load(openfile)


    newData = {'Ano': ano, 'Min': len(topBytes) - 200, 'Max': len(topBytes) - 1} #Aqui vem a nova data que deve ser concatenada

    fileBytes.append(newData)#concatena o que ja tinha no arquivo binario com a nova data
    with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
        pickle.dump(fileBytes, openfile)


    #-----------------------------------------------------------------------------
    #Cria e ordena o topMusicas - Reaproveitada da criação de arquivos
    #-----------------------------------------------------------------------------
    itera = len(topMusicas)
    for x in top:
        topMusicas.append((itera, x['Pontos']))
        if(itera < len(topMusicas)-1): #Vai incrementando ate chegar no final da lista
            itera += 1

    topMusicas.sort(key=lambda tup: tup[1], reverse=True)  #Faz um sort usando o elemento [1] (pontos) da tupla como criterio de ordenacao

    #Salva ranking geral de musicas
    with (open("topMusicas.bin", 'wb+')) as openfile:
        pickle.dump(topMusicas, openfile)

    topArtistas.sort(key=lambda tup: tup[1], reverse=True)  #Faz um sort usando o elemento [1] (pontos) da tupla como criterio de ordenacao

    #Salva ranking geral de artistas
    with (open("topArtistas.bin", 'wb+')) as openfile:
        pickle.dump(topArtistas, openfile)

    #-----------------------------------------------------------------------------
    #Inserindo nas arvores TRIE
    #-----------------------------------------------------------------------------
    for x in range(indIni, len(topBytes)):
        addString(trieMusicas, str(topBytes[x]['Titulo']), x)
        addString(trieArtistas, topBytes[x]['Artista'], x)

    filename = "trieMusicas.bin"
    with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
        pickle.dump(trieMusicas, openfile)

    filename = "trieArtistas.bin"
    with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
        pickle.dump(trieArtistas, openfile)


#aceita como entrada strings nos atributos de artista e titulos e ints nos de ano,pontos,peak e semanas
def adicionaReg(artista, titulo, ano, pontos, peak, semanas):
    reg = {} #Cria o dicionario com a entrada atual
    #Adiciona os parametros ao dicionario
    reg['Artista'] = artista
    reg['Titulo'] = titulo
    reg['Ano'] = ano
    reg['Pontos'] = pontos
    reg['Peak'] = peak
    reg['Semanas'] = semanas


    #inserindo no database
    database.append(reg)
    with (open('database.bin', 'wb+')) as openfile: #abre o arquivo no modo de leitura binaria 'wb' como openfile
        pickle.dump(database, openfile)

    #inserindo no arquivo de indices
    indNew = {}
    indNew['Ano'] = reg['Ano']
    indNew['Min'] = (len(database) - 1)
    indNew['Max'] = (len(database) - 1)

    indices.append(indNew)
    with (open('indices.bin', 'wb+')) as openfile: #abre o arquivo no modo de leitura binaria 'wb' como openfile
        pickle.dump(indices, openfile)

    #inserindo no topArtistas
    indArtista = -1 #flag que salva o indice do artista iterado, se for -1 o artista nao esta na lista
    indice = 0 #indice que esta procurando o artista
    for x in topArtistas: #percorre o arquivo topArtistas procurando pelo artista
        if x[0] == reg['Artista']:
            indArtista = indice
        indice += 1

    if(indArtista != -1): #Se o artista ja esta na lista
        topArtistas[indArtista] = (reg['Artista'], topArtistas[indArtista][1] + reg['Pontos'])
    else: #cria um novo artista
        topArtistas.append((reg['Artista'], reg['Pontos'])) #da um append com a tupla 'nome artista' + 'pontos'

    topArtistas.sort(key=lambda tup: tup[1], reverse=True)  #Faz um sort usando o elemento [1] (pontos) da tupla como criterio de ordenacao
    #Salva ranking geral de artistas
    with (open("topArtistas.bin", 'wb+')) as openfile:
        pickle.dump(topArtistas, openfile)

    #inserindo no topMusicas
    topMusicas.append((len(database)-1, reg['Pontos']))
    topMusicas.sort(key=lambda tup: tup[1], reverse=True)  #Faz um sort usando o elemento [1] (pontos) da tupla como criterio de ordenacao

    #Salva ranking geral de musicas
    with (open("topMusicas.bin", 'wb+')) as openfile:
        pickle.dump(topMusicas, openfile)


    #inserindo nas arvores TRIE
    addString(trieMusicas, str(reg['Titulo']), len(database)-1)
    addString(trieArtistas, reg['Artista'], len(database)-1)

    filename = "trieMusicas.bin"
    with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
        pickle.dump(trieMusicas, openfile)

    filename = "trieArtistas.bin"
    with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
        pickle.dump(trieArtistas, openfile)









'''

    Definições da GUI

'''

welcomeMessage = "Bem-vindo ao Billboard 100!" + \
                 "\n\nPara continuar, selecione a query desejada e digite as entradas requisitadas.\n\n" + \
                 "Projeto no GitHub: https://github.com/Rafaelfferreira/CPD\n\n" + \
                 "Devs: \nFelipe Colombelli: https://github.com/colombelli/\nRafael Ferreira: https://github.com/Rafaelfferreira/\n\n" + \
                 "Testers: \nVítor Matias: https://github.com/VitorCMatias"


# Função responsável por inserir mais dados no database
def insereNovosDados():
    window.fileName = filedialog.askopenfilename()
    adicionaAno(window.fileName)
    return


# Função responsável por inserir novo registro (único)
def insereNovoRegistro():

    reg = Tk()

    # definição do tamanho da janela
    width_window = 345
    height_window = 155

    # pega tamanho da tela do usuário
    screenW = window.winfo_screenwidth()
    screenH = window.winfo_screenheight()

    # coordenadas para centralizar janela
    xpos = (screenW/2) - (width_window/2)
    ypos = (screenH/2) - (height_window/2)

    # seta tamanho da janela e posição na tela
    reg.geometry("%dx%d+%d+%d" % (width_window, height_window, xpos, ypos))
    reg.resizable(width=False, height=False)   # desbilita ajuste de tamanho da janela
    reg.iconbitmap('b_icon.ico')
    reg.wm_title("Inserção de Registro")

    """

        Inputs

    """

    # mensagem pedindo primeiro input
    Label (reg, text="Artista:", bg="white", fg="black", font="none 10") .grid(row=0, column=0, sticky=W, padx=4)
    # texto de entrada 1
    input1 = Entry(reg, font="none 11", bg="white")
    # o padx no grid determina um espaçamento
    input1.grid(row=1, column=0, sticky=EW, padx=4)   # grid definido aqui embaixo para não bugar o método get()


    # mensagem pedindo segundo input
    Label (reg, text="Música:", bg="white", fg="black", font="none 10") .grid(row=0, column=1, sticky=W, padx=4)
    input2 = Entry(reg, font="none 11", bg="white")
    input2.grid(row=1, column=1, sticky=EW, padx=4)


    # mensagem pedindo terceiro input
    Label (reg, text="Ano:", bg="white", fg="black", font="none 10") .grid(row=2, column=0, sticky=W, padx=4)
    input3 = Entry(reg, font="none 11", bg="white")
    input3.grid(row=3, column=0, sticky=EW, padx=4)


    # mensagem pedindo quarto input
    Label (reg, text="Pontos:", bg="white", fg="black", font="none 10") .grid(row=2, column=1, sticky=W, padx=4)
    input4 = Entry(reg, font="none 11", bg="white")
    input4.grid(row=3, column=1, sticky=EW, padx=4)


    # mensagem pedindo quinto input
    Label (reg, text="Peak:", bg="white", fg="black", font="none 10") .grid(row=4, column=0, sticky=W, padx=4)
    input5 = Entry(reg, font="none 11", bg="white")
    input5.grid(row=5, column=0, sticky=EW, padx=4)


    # mensagem pedindo sexto input
    Label (reg, text="Semanas:", bg="white", fg="black", font="none 10") .grid(row=4, column=1, sticky=W, padx=4)
    input6 = Entry(reg, font="none 11", bg="white")
    input6.grid(row=5, column=1, sticky=EW, padx=4)



    B1 = ttk.Button(reg, text="Inserir", command = lambda: pegaInputAdiciona(input1, input2, input3, input4, input5, input6, reg))
    B1.grid(row=6, column=0, columnspan=2, sticky=EW, padx=4)
    reg.mainloop()

    return


def pegaInputAdiciona(input1, input2, input3, input4, input5, input6, window):

    # pega os inputs
    artista = input1.get()
    titulo = input2.get()
    ano = int(input3.get())
    pontos = int(input4.get())
    peak = int(input5.get())
    semanas = int(input6.get())

    # chama função que insere o registro passando os parâmetros
    adicionaReg(artista, titulo, ano, pontos, peak, semanas)
    window.destroy()

    return




# Função acionada no click de Help
def helpMenu():

    help = Tk()

    # definição do tamanho da janela
    width_window = 300
    height_window = 300

    # pega tamanho da tela do usuário
    screenW = window.winfo_screenwidth()
    screenH = window.winfo_screenheight()

    # coordenadas para centralizar janela
    xpos = (screenW/2) - (width_window/2)
    ypos = (screenH/2) - (height_window/2)

    # seta tamanho da janela e posição na tela
    help.geometry("%dx%d+%d+%d" % (width_window, height_window, xpos, ypos))
    help.resizable(width=False, height=False)   # desbilita ajuste de tamanho da janela
    help.iconbitmap('b_icon.ico')
    help.wm_title("Help")
    help.configure(background='white')

    texto = "Este programa foi feito com o intuito de... \nPara usar... Você pode... Quem fez... etc"

    label = Label(help, text=texto, bg="white") .grid(row=0, column=0, padx=10, pady=10)


    help.mainloop()


    return


# Popup de erro, recebe uma string (mensagem de erro) e exibe em uma nova janela esta mensagem
def popupErro(msg):
    popup = Tk()

    # definição do tamanho da janela
    width_window = 215
    height_window = 70

    # pega tamanho da tela do usuário
    screenW = window.winfo_screenwidth()
    screenH = window.winfo_screenheight()

    # coordenadas para centralizar janela
    xpos = (screenW/2) - (width_window/2)
    ypos = (screenH/2) - (height_window/2)

    # seta tamanho da janela e posição na tela
    popup.geometry("%dx%d+%d+%d" % (width_window, height_window, xpos, ypos))
    popup.resizable(width=False, height=False)   # desbilita ajuste de tamanho da janela
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

        ano = input2.get()
        try:   # tenta converter a string de entrada para número inteiro
            n = int(string)
            ano = int(ano)

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return


        resultado = relevanciaArtistaAno(database, indices, ano, n, reverse)



# Query das músicas mais relevantes (ano/artista opcionais)
    elif option == QUERIES[2]:

        # tenta converter a quantidade
        try:
            n = int(string)
            ano = str(input2.get())

            if ano == "":   # se não entrou com um ano, ele recebe None
                ano = None
            else:  # se entrou com um ano, tenta converter pra int
                ano = int(ano)

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        # pega o input do artista (opcional)
        artista = str(input3.get())

        # caso não tenham sido fornecidos, a entrada para a função deve ser None
        if artista == "":
            artista = None

        # checa se busca reversa
        if reverse:
            resultado = relevanciaReversa(trieArtistas, topMusicas, indices, database, n, ano, artista)
        else:
            resultado = relevancia(trieArtistas, topMusicas, indices, database, n, ano, artista)



# Query que retorna o artista mais popular e quantas semanas ele ficou na billboard
    elif option == QUERIES[3]:

        artista1 = string
        artista2 = input2.get()

        outputQuery4 = comparaRelevArtista(trieArtistas, database, artista1, artista2)

        # testa se retornou algum artista na string de retorno
        if "Nenhum artista foi encontrado" in outputQuery4:
            resultado = outputQuery4

        else:   # se retornou
            # formatção de saída da query:
            resultado = "Artista mais relevante: " + outputQuery4[0] + \
                        "\nTotal de semanas que ficou na Billboard: " + str(outputQuery4[1])



# Query que retorna a música mais popular e quantas semanas ela ficou na billboard
    elif option == QUERIES[4]:

        musica1 = string
        artista1 = input2.get()
        musica2 = input3.get()
        artista2 = input4.get()

        outputQuery4 = comparaRelevMusica(trieMusicas, database, musica1, artista1, musica2, artista2)

        # testa se retornou algum artista na string de retorno
        if outputQuery4 == None:
            resultado = "Nenhuma música com esse artista foi encontrada.\nTente usar a opção de sugestão de músicas para receber sugestão de músicas que constam na base de dados."

        else:   # se retornou
            # formatção de saída da query:
            resultado = "Música mais relevante: " + outputQuery4[0] + \
                        "\nTotal de semanas que ficou na Billboard: " + str(outputQuery4[1])



# Query que retorna sugestão de artistas dado uma substring/tentatica de busa de artista
    elif option == QUERIES[5]:
        try:   # tenta converter o input de máximo de sugestões para int
            n = int(input2.get())
        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        resultado = "Sugestão de artistas:\n" + \
            outputSugestoesLista(findString(1, database, trieArtistas, string, n)[1])

# Query que sugere músicas dado uma substring/tentativa de busca de música
    elif option == QUERIES[6]:
        try:   # tenta converter o input de máximo de sugestões para int
            n = int(input2.get())
        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return
        resultado = "Sugestão de músicas:\n" + \
            outputSugestoesLista(findString(0, database, trieMusicas, string, n)[1])



# Query que lista as músicas de um dado artista
    elif option == QUERIES[7]:
        resultado = listaMusicasArtista(database, trieArtistas, string)




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
        input2.delete(0, 'end')
        input2.config(state=DISABLED)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)


        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Quantidade de artistas:')
        msgInput2.config(text='')
        msgInput3.config(text='')
        msgInput4.config(text='')


    # query: "Os n artistas mais relevantes do ano"
    if selection == QUERIES[1]:

        # primeira e segunda caixas habilitadas
        input2.config(state=NORMAL)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)


        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Quantidade de artistas:')
        msgInput2.config(text='Ano:')
        msgInput3.config(text='')
        msgInput4.config(text='')


    # query: Busca das músicas mais relevantes
    if selection == QUERIES[2]:

        # somente última caixa desabilitada
        input2.config(state=NORMAL)
        input3.config(state=NORMAL)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Quantidade de músicas:')
        msgInput2.config(text='Ano (opcional):')
        msgInput3.config(text='Artista (opcional):')
        msgInput4.config(text='')


    # query: retorna o artista mais popular e quantas semanas ele ficou na billboard
    if selection == QUERIES[3]:

        # primeira e segunda caixas habilitadas
        input2.config(state=NORMAL)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Artista 1:')
        msgInput2.config(text='Artista 2:')
        msgInput3.config(text='')
        msgInput4.config(text='')


    # query: retorna a música mais popular e quantas semanas ela ficou na billboard
    if selection == QUERIES[4]:

        # todas as caixas habilitadas
        input2.config(state=NORMAL)
        input3.config(state=NORMAL)
        input4.config(state=NORMAL)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Música 1:')
        msgInput2.config(text='Artista 1:')
        msgInput3.config(text='Música 2:')
        msgInput4.config(text='Artista 2:')



    # query: sugestão de artistas
    if selection == QUERIES[5]:

        # só a primeira caixa habilitada
        input2.config(state=NORMAL)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Artista')
        msgInput2.config(text='Quantidade máxima de sugestões')
        msgInput3.config(text='')
        msgInput4.config(text='')


    # query: Sugestão de músicas
    if selection == QUERIES[6]:

        # só a primeira caixa habilitada
        input2.config(state=NORMAL)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)

        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Música:')
        msgInput2.config(text='Quantidade máxima de sugestões')
        msgInput3.config(text='')
        msgInput4.config(text='')


    #query: Lista de músicas de um dado artista
    if selection == QUERIES[7]:

        # só a primeira caixa habilitada
        input2.delete(0, 'end')
        input2.config(state=DISABLED)
        input3.delete(0, 'end')
        input3.config(state=DISABLED)
        input4.delete(0, 'end')
        input4.config(state=DISABLED)


        # troca mensagens das labels de instrução de input
        msgInput1.config(text='Artista')
        msgInput2.config(text='')
        msgInput3.config(text='')
        msgInput4.config(text='')


# main
window = Tk()

# definição do tamanho da janela
width_window = 505
height_window = 530

# pega tamanho da tela do usuário
screenW = window.winfo_screenwidth()
screenH = window.winfo_screenheight()

# coordenadas para centralizar janela
xpos = (screenW/2) - (width_window/2)
ypos = (screenH/2) - (height_window/2)

# seta um título na janela
window.title("Billboard 100")
# seta tamanho da janela e posição na tela
window.geometry("%dx%d+%d+%d" % (width_window, height_window, xpos, ypos))
# seta cor de fundo da janela
window.configure(background="white")
# bloqueia redimensionamento da janela
window.resizable(width=False, height=False)
# define icone da janela
window.iconbitmap('b_icon.ico')



"""

    Criação do menu dropdown para inserção de arquivos

"""

menu = Menu(window) # menu topo da janela
window.config(menu=menu)

subMenu = Menu(menu, tearoff=0) # submenu dropdown
menu.add_cascade(label="File", menu=subMenu)
menu.add_command(label="Help", command=helpMenu)

subMenu.add_command(label="Inserir dados", command=insereNovosDados)
subMenu.add_command(label="Inserir registro", command=insereNovoRegistro)
subMenu.add_separator()
subMenu.add_command(label="Exit", command=window.destroy)



"""

    Restante dos elementos da janela

"""



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
    QUERIES[1],
    QUERIES[2],
    QUERIES[3],
    QUERIES[4],
    QUERIES[5],
    QUERIES[6],
    QUERIES[7]
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
msgInput1 = Label (window, text="Quantidade de artistas:", bg="white", fg="black", font="none 10")
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
