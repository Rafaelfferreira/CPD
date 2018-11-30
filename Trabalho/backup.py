

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
