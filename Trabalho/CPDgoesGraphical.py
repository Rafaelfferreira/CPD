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



# DEFINE DAS QUERIES:
QUERIES = [

    "Os n artistas mais relevantes",
    "Os 10 artistas mais relevantes do ano"

]



'''

    FUNÇÕES NECESSÁRIAS PARA MEXER COM A ÁRVORE TRIE

'''

class TrieNode(object):


    def __init__(self, char: str):   # __init__ é um método especial para fazer construtores
        self.char = char   # caractere do nodo atual
        self.filhos = []   # nodos filhos
        self.pFinalizada = False   # se é o último nodo e a palavra terminou
        self.indices = []   # lista vazia para nodos que não são término de palavra
        ### não é um índice único e sim uma lista, pois podem existir títulos de música repetidos com mais de um artista


#Definindo função que localiza uma string na arvore
def findString(select, dados, raiz, palavra: str) -> (bool, []):
    """
      1. Se a palavra existe e tem algum índice associado, retorna verdadeiro e a lista de índices dela
      2. Se a palavra não existe, retorna falso e uma lista com sugestões de palavras

      Sendo o parâmetro select utilizada para indicar se a busca é por artista ou música (0 música, 1 artista)
    """
    palavra = formataString(palavra)   # formata string de entrada para o padrão (todas as letras maiúsculas sem acento)
    nodo = raiz
    stringSugerida = ""  # guarda os caracteres já encontrados para sugerir os próximos

    if not raiz.filhos:   # se o nodo raiz não tiver nenhum filho, trivial, retorna falso
        return False, []
    for char in palavra:
        charNaoEncontrado = True
        for filho in nodo.filhos:
            if filho.char == char:
                charNaoEncontrado = False   # assinala que o char foi encontrado
                stringSugerida = stringSugerida+char
                nodo = filho   # passa iteração para o nodo filho
                break

        if charNaoEncontrado:   # chama a função que procura sugestões e retorna a tupla (False, lista de sugestões)
            return False, sugereStrings(select, dados, nodo, stringSugerida, 15)

    # Caso passe por todos os caracteres sem retornar false, então significa que a palavra foi encontrada
    # Resta saber se aquele nodo é um nodo final com um índice associado
    if nodo.pFinalizada:
        return True, nodo.indices
    else:
        return False, sugereStrings(select, dados, nodo, stringSugerida, 15)

# Função que formata string desconsiderando maiúsculas e minúsculas e que remove acentos
def formataString(string):
    string = normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')
    return string.upper()

def sugereStrings(select, dados, nodo, string, maxSugestoes):   # onde select igual a 1 significa que se procura um artista e False, música
        listaDeSugestoes = []   # cria lista vazia para adicionarmos as sugestões
        procuraSugestoes(nodo, string, listaDeSugestoes)   # chama a função que percorre a trie procurando sugestões

        itera = copy.deepcopy(listaDeSugestoes)   # utilizado para iteração na lista que está sendo modificada enquanto o loop itera

        # substitui os indices pelos títulos
        for indice in itera:
            listaDeSugestoes.remove(indice)   # remove o índice
            if select:
                listaDeSugestoes.append(dados[indice]['Artista'])
            else:
                listaDeSugestoes.append(dados[indice]['Titulo'])


        listaDeSugestoes = sorted(listaDeSugestoes)   # ordena a lista alfabeticamente
        return listaDeSugestoes[:maxSugestoes]   # retorna apenas os n elementos da lista definidos por maxSugestoes


# função que dado um nodo, uma parte correta de uma string (que existe na TRIE), uma lista de sugestoes, retorna uma lista de sugestões
def procuraSugestoes(nodo, string, listaDeSugestoes):

        if nodo.pFinalizada:
            listaDeSugestoes.append(nodo.indices[0])   # adiciona nova sugestão na lista

        for filho in nodo.filhos:
            procuraSugestoes(filho, string+filho.char, listaDeSugestoes)   # recursão para cada filho

        return

def retiraFeaturing(artistaString):

    if " Featuring" in artistaString:   # Se a música tiver um featuring, deve-se retirá-lo
            indexFeat = artistaString.find(" Featuring")   # pega índice do char space antes de Featuring
            artistaString = artistaString[:indexFeat]   # retorna apenas o primeiro artista

    return artistaString   # caso não caia no if, simplesmente retorna o artista assim como veio




'''

    LEITURA DOS ARQUIVOS

'''

#Faz a leitura do arquivo de registros
with (open('database.bin', 'rb')) as openfile:
    dados = pickle.load(openfile)

#Leitura do arquivo de indices de anos
with (open('indices.bin', 'rb')) as openfile:
    indices = pickle.load(openfile)

#Leitura do arquivo com a arvore TRIE de titulos de musicas
with open('trieMusicas.bin','rb') as openfile:
    trieMusicas = pickle.load(openfile)

#Leitura do arquivo com a arvore TRIE de nomes de artistas
with open('trieArtistas.bin','rb') as openfile:
    trieArtistas = pickle.load(openfile)

#Leitura do arquivo com o top 200 geral
with open('topMusicas.bin','rb') as openfile:
    topMusicas = pickle.load(openfile)







'''

    Query que retorna os N artistas mais relevantes no geral

'''


def topArtistas(n):   # sendo n o número máximo de artistas

    if os.path.exists("topArtistas.bin"): #confere se o arquivo existe
        with open("topArtistas.bin",'rb') as openfile:  #with automaticamente da um close() no final
            topArtistas = pickle.load(openfile)

    topArtistas = topArtistas[:n]   # pega só os n relevantes

    stringFinal = ""
    counter = 1

    # transforma numa string para poder ser inserida no output da text box
    for artista in topArtistas:
        stringFinal = stringFinal + str(counter) + ". " + artista[0] + " \n   Pontuação: " + str(artista[1]) + "\n\n"
        counter += 1

    return stringFinal





'''

    Query que retorna os 10 artistas mais relevantes de determinado ano

'''


def relevanciaArtistaAno(dados, indiceFile, ano, maxArtistas):
    maxArtistas = 10    # fixado em 10 mas passível de mudança futuramente

    # Loop que pega o ano passado para procurar no arquivo principal o artista mais relevante
    for entrada in range(len(indiceFile)):
        print(indiceFile[entrada]['Ano'])
        if indiceFile[entrada]['Ano'] == ano:
            index = entrada
            indexMin = indiceFile[index]['Min']
            indexMax = indiceFile[index]['Max']

    artistasDict = {}

    # Itera pelos indices daquele determinado ano construindo um dicionário de artistas e pontos acumulados
    while indexMin <= indexMax:

        artistaIterado = retiraFeaturing(dados[indexMin]['Artista'])
        if artistaIterado in artistasDict:
            artistasDict[artistaIterado] += dados[indexMin]['Pontos']
        else:
            artistasDict[artistaIterado] = dados[indexMin]['Pontos']

        indexMin += 1

    #artistasDict = sorted(artistasDict.items(), key = lambda tup: (tup[1]["Pontos"]), reverse=True)
    dictSorted = sorted(artistasDict.items(), key=lambda kv: kv[1], reverse=True)

    dictSorted = dictSorted[:maxArtistas]

    stringFinal = "Artistas mais relevantes de " + str(ano) + "\n\n"
    counter = 1

    # transforma numa string para poder ser inserida no output da text box
    for artista in topArtistas:
        stringFinal = stringFinal + str(counter) + ". " + artista[0] + " \n   Pontuação: " + str(artista[1]) + "\n\n"
        counter += 1

    return stringFinal













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

        resultado = topArtistas(n)

# Query dos 10 artistas mais relevantes de determinado ano:
    elif option == QUERIES[1]:

        try:   # tenta converter a string de entrada para número inteiro
            ano = int(string)

            # testa se é um ano válido
######################   IMPLEMENTAR   #########################################################################

        except ValueError:   # se não der, popa uma mensagem de erro
            popupErro("Você deve fornecer um número inteiro!")
            return

        resultado = relevanciaArtistaAno(dados, indices, ano, 10)




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
