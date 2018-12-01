import copy
from unicodedata import normalize


'''''''''''''''

 Criando as funções necessárias para acessar as árvores TRIE

'''''''''''''''

class TrieNode(object):


    def __init__(self, char: str):   # __init__ é um método especial para fazer construtores
        self.char = char   # caractere do nodo atual
        self.filhos = []   # nodos filhos
        self.pFinalizada = False   # se é o último nodo e a palavra terminou
        self.indices = []   # lista vazia para nodos que não são término de palavra
        ### não é um índice único e sim uma lista, pois podem existir títulos de música repetidos com mais de um artista


#Definindo função que localiza uma string na arvore
def findString(select, dados, raiz, palavra: str, maxSugestoes=15) -> (bool, []):
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
            return False, sugereStrings(select, dados, nodo, stringSugerida, maxSugestoes)

    # Caso passe por todos os caracteres sem retornar false, então significa que a palavra foi encontrada
    # Resta saber se aquele nodo é um nodo final com um índice associado
    if nodo.pFinalizada:
        return True, nodo.indices
    else:
        return False, sugereStrings(select, dados, nodo, stringSugerida, maxSugestoes)


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
                listaDeSugestoes.append(str(dados[indice]['Artista']))
            else:
                listaDeSugestoes.append(str(dados[indice]['Titulo']))


        listaDeSugestoes = sorted(listaDeSugestoes)   # ordena a lista alfabeticamente
        return listaDeSugestoes[:maxSugestoes]   # retorna apenas os n elementos da lista definidos por maxSugestoes


# função que dado um nodo, uma parte correta de uma string (que existe na TRIE), uma lista de sugestoes, retorna uma lista de sugestões
def procuraSugestoes(nodo, string, listaDeSugestoes):

        if nodo.pFinalizada:
            listaDeSugestoes.append(nodo.indices[0])   # adiciona nova sugestão na lista

        for filho in nodo.filhos:
            procuraSugestoes(filho, string+filho.char, listaDeSugestoes)   # recursão para cada filho

        return
