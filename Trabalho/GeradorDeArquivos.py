#importa as bibliotecas
import pandas as pd
import xlrd
import pickle #modulo usado para serializar dados para o arquivo binario
import os
import time
from unicodedata import normalize #biblioteca usada para criar as arvores TRIE

#Le o excel para a variavel df
df = pd.read_excel('Hot Stuff.xlsx')

#Funcao que retira as features de artistas selecionados e salva apenas o artista principal da musica
def retiraFeaturing(artistaString):
    
    if " Featuring" in artistaString:   # Se a música tiver um featuring, deve-se retirá-lo
            indexFeat = artistaString.find(" Featuring")   # pega índice do char space antes de Featuring
            artistaString = artistaString[:indexFeat]   # retorna apenas o primeiro artista
        
    return artistaString   # caso não caia no if, simplesmente retorna o artista assim como veio

# Função que formata string desconsiderando maiúsculas e minúsculas e que remove acentos
def formataString(string):
    string = normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')
    return string.upper()

#------------------------------------------------------------
#Definicao das funcoes usadas para gerar as arvores TRIE
#------------------------------------------------------------
#Definicao da classe de nodo das arvores TRIE
class TrieNode(object):
    def __init__(self, char: str):   # __init__ é um método especial para fazer construtores
        self.char = char   # caractere do nodo atual
        self.filhos = []   # nodos filhos
        self.pFinalizada = False   # se é o último nodo e a palavra terminou
        self.indices = []   # lista vazia para nodos que não são término de palavra
        ### não é um índice único e sim uma lista, pois podem existir títulos de música repetidos com mais de um artista

#Definicao da funcao que adiciona uma string na arvore TRIE
def addString(raiz, palavra: str, indice: int):   # função usada para adicionar uma palavra nova à estrutura trie 
    palavra = formataString(palavra)   # formata string de entrada para o padrão (todas as letras maiúsculas sem acento)
    nodo = raiz
    for char in palavra:
        encontradoEmFilho = False
        # busca pelo caractere nos filhos do nodo atual
        for filho in nodo.filhos:
            if filho.char == char: 
                nodo = filho   # apontamos o nodo para o filho que contém esse char
                encontradoEmFilho = True
                break
        
        if not encontradoEmFilho:   # se o caractere não foi encontrado, adiciona novo filho
            novoNodo = TrieNode(char)
            nodo.filhos.append(novoNodo)
            nodo = novoNodo   # apontamos, então, o nodo para seu novo filho e continuamos a iteração
    
    nodo.pFinalizada = True   # indica que até ali pode ser uma palavra (nome de música/artista completo)
    nodo.indices.append(indice)   # assinala o indice passado
    
#Funcao que procura uma string na arvore TRIE 
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
    
#Funcoes utilizadas para sugerir buscas
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
            if filho.pFinalizada:   
                listaDeSugestoes.append(filho.indices[0])   # adiciona nova sugestão na lista
                
        return

#esta celula calcula o quao popular foi uma musica no mes especificado (Maio de 1990) atribuindo um sistema de pontos baseado em que posicao ela ficou no top 100 em cada semana do mês
#vai contar o quao popular foi a musica no ano atribuindo pontos a quantas semanas ela ficou entre as mais tocadas
#testando se o char especificado esta na entrada atual
#pode ser usado para identificar anos diferentes

tempo = time.time() #Armazena o tempo de inicio do processamento
topArtistas = {}
topMusicas = {}
for ano in range(1960,2016):
    contador = {}
    topMusicas = {} #ESSA LINHA É POTENCIALMENTE INUTIL #cria um dicionario para guardar o top músicas no geral
    #Salva os registros do ano atual
    for i in range(len(df)):
        
        if (str(ano) + '-') in df['WeekID'][i]: #filtra todas as entradas por ano E mes nesse caso (Maio de 1990)
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
        if artistaIterado in topArtistas:   # testa se o artista já está no dicionário
            topArtistas[artistaIterado] += top[i]['Pontos']   # se sim só soma nos seus pontos
        else:   # caso não esteja, adicona
            topArtistas[artistaIterado] = top[i]['Pontos']     
    
    #Concatena o dicionario no arquivo teste.bin
    filename = 'database.bin'
    topBytes = []
    

    if os.path.exists(filename): #confere se o arquivo existe
        with open(filename,'rb') as openfile:  #with automaticamente da um close() no final
            topBytes = pickle.load(openfile) #carrega o que ja esta salvo no arquivo


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
#Ordena o dicionário de artistas
#-----------------------------------------------------------------------------
artistasSorted = sorted(topArtistas.items(), key=lambda kv: kv[1], reverse=True)
    
#Salva ranking geral de artistas
with (open("topArtistas.bin", 'wb+')) as openfile:
    pickle.dump(artistasSorted, openfile)
#-----------------------------------------------------------------------------
#Cria e ordena o topMusicas
#-----------------------------------------------------------------------------
itera = 0
for x in topBytes:
    topMusicas[itera] = x['Pontos']
    itera += 1    
    
topMusicasSorted = sorted(topMusicas.items(), key=lambda kv: kv[1], reverse=True)

#Salva ranking geral de musicas
with (open("topMusicas.bin", 'wb+')) as openfile:
    pickle.dump(topMusicasSorted, openfile)    

#-----------------------------------------------------------------------------
#Cria as arvores TRIE
#-----------------------------------------------------------------------------
raizMusicas = TrieNode('@')   # raiz da trie de músicas 
raizArtistas = TrieNode('@')  # raiz da trie de artistas

indice = 0   # endereço da música no arquivo

for x in topBytes:  
    # o str é necessário para os casos em que a música ou artista são apenas números e interpretados com inteiros
    addString(raizMusicas, str(x['Titulo']), indice)   
    addString(raizArtistas, retiraFeaturing(str(x['Artista'])), indice)
    indice += 1
    
filename = "trieMusicas.bin"
with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
    pickle.dump(raizMusicas, openfile)
    
filename = "trieArtistas.bin"
with (open(filename, 'wb+')) as openfile: #abre o arquivo de teste no modo de leitura binaria 'wb' como openfile
    pickle.dump(raizArtistas, openfile)
    
#Retorna o tempo passado desde que o programa comecou a rodar
t = time.time() - tempo #Salva em t o tempo que o processo levou
print('Tempo levado para gerar os arquivos: ', t, 'segundos')