import pickle
import copy
from unicodedata import normalize
from TRIE import *



# função que recebe a lista de sugestão e retorna uma string com todos os elementos separados por vírgula
def outputSugestoesLista(lista):

    stringOut = ""

    for elemento in lista:
        stringOut = stringOut + "\n" + str(elemento)

    return stringOut


# função que returna string com mensagem de artista não encontrado e lista sugestões
def sugestoesArtistas(listaArtistas):

    stringOut = 'Artista não encontrado\nSugestões de artistas:\n' + outputSugestoesLista(listaArtistas)

    return stringOut


# função que formata a saída das queries de relevancia e relevancia inversa
def arrumaStringRelevancia(listaDicios):

    stringOut = "Músicas mais relevantes:\n\n"

    # se o retorno é um único valor, transforma esse valor em lista para não bugar a iteração for
    if type(listaDicios) != list:
        listaDicios = [listaDicios]


    counter = 1
    # transforma numa string para poder ser inserida no output da text box
    for musica in listaDicios:
        stringOut = stringOut + str(counter) + ". " +       \
            musica['Artista'] + " - " + musica['Titulo'] + "\n   Ano: " + str(musica['Ano']) +      \
            "   Pontuação: " + str(musica['Pontos']) + "\n\n"
        counter += 1


    return stringOut



'''''''''''''''

Definição das Querys

'''''''''''''''

# Query que retorna um numero N de pesquisas em ordem de relevancia, filtrando por artista/ano opcionalmente

def relevancia(trieArtistas, topMusicas, indices, dados, top, ano=None, artista=None):

    outputList = []

    if(top < 1):
    	return "Você deve inserir um valor válido na quantidade de itens a ser retornado."

    #Retornando de um determinado ano
    if(ano != None and artista == None):
        #Consultando do arquivo de indices qual o index inicial do ano que o usuario entrou
        comeco = -1 #Se estiver em -1 eh pq nao encontrou o ano
        for x in indices:
            if x['Ano'] == ano:
                comeco = x['Min']
        if(comeco != -1):
            for i in range(comeco, comeco+top):
                outputList.append(dados[i])
            return arrumaStringRelevancia(outputList)
        else:
            return "O ano inserido não consta na base de dados."

    #Retornando de um determinado artista
    if(artista != None and ano == None):
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            return sugestoesArtistas(indicesArtista)
        else:
            listaMusicas2 = []
            for i in indicesArtista:
                listaMusicas2.append(dados[i])

            listaMusicas = copy.deepcopy(listaMusicas2) #Faz uma copia de lista2 para lista, pq lista2 so referencia os registros de dados ao inves de criar eles novamente

            for i in range(len(listaMusicas)-1):
                for j in range(i+1, len(listaMusicas)-1):
                    if(listaMusicas[i]['Titulo'] == listaMusicas[j]['Titulo']):
                        listaMusicas[i]['Pontos'] = listaMusicas[i]['Pontos'] + listaMusicas[j]['Pontos']
                        listaMusicas.pop(j)

            listaMusicas = sorted(listaMusicas, key = lambda tup: (tup["Pontos"]), reverse=True)

            if(len(listaMusicas) < top): #Faz com que a query retorne apenas o numero de entradas pedido na variavel top
                top = len(listaMusicas)

            for i in range(top):
                outputList.append(listaMusicas[i])
            return arrumaStringRelevancia(outputList)

    #Retorna o top geral
    if(ano == None and artista == None):
        for i in range(top):
            outputList.append(dados[topMusicas[i][0]])
        return arrumaStringRelevancia(outputList)

    #Retorna o top dos artistas em determinado ano
    if(artista != None and ano != None):
        #Faz o mesmo procedimento que a busca por artista
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            return sugestoesArtistas(indicesArtista)
        else:
            listaMusicas2 = []
            for i in indicesArtista:
                listaMusicas2.append(dados[i])

            listaMusicas = copy.deepcopy(listaMusicas2) #Faz uma copia de lista2 para lista, pq lista2 so referencia os registros de dados ao inves de criar eles novamente

            for i in range(len(listaMusicas)-1):
                for j in range(i+1, len(listaMusicas)-1):
                    if(listaMusicas[i]['Titulo'] == listaMusicas[j]['Titulo']):
                        listaMusicas[i]['Pontos'] = listaMusicas[i]['Pontos'] + listaMusicas[j]['Pontos']
                        listaMusicas.pop(j)

            listaMusicas = sorted(listaMusicas, key = lambda tup: (tup["Pontos"]), reverse=True)

            listaMusicasAno = [] #Lista com as musicas do artista no ano pedido

            for i in range(len(listaMusicas)):
                if(listaMusicas[i]['Ano'] == ano):
                    listaMusicasAno.append(listaMusicas[i])

            if(len(listaMusicasAno) < top):
                top = len(listaMusicasAno)
            if(len(listaMusicasAno) > 0):
                for i in range(top):
                    outputList.append(listaMusicasAno[i])
                    return arrumaStringRelevancia(outputList)
            else:
                return "O artista não teve nenhuma música no top 200 da Billboard para este ano."



def relevanciaReversa(trieArtistas, topMusicas, indices, dados, top, ano=None, artista=None):

    outputList = []

    if(top < 1):
        return "Você deve inserir um valor válido na quantidade de itens a ser retornado."

    #Retornando de um determinado ano
    if(ano != None and artista == None):
        #Consultando do arquivo de indices qual o index inicial do ano que o usuario entrou
        comeco = -1 #Se estiver em -1 eh pq nao encontrou o ano
        for x in indices:
            if x['Ano'] == ano:
                comeco = x['Max']
        if(comeco != -1):
            for i in range(comeco, comeco-top, -1): #(start,stop,step)
                outputList.append(dados[i])
            return arrumaStringRelevancia(outputList)
        else:
            return "O ano inserido não consta na base de dados."

    #Retornando de um determinado artista
    if(artista != None and ano == None):
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            return sugestoesArtistas(indicesArtista)
        else:
            listaMusicas2 = []
            for i in indicesArtista:
                listaMusicas2.append(dados[i])

            listaMusicas = copy.deepcopy(listaMusicas2) #Faz uma copia de lista2 para lista, pq lista2 so referencia os registros de dados ao inves de criar eles novamente

            for i in range(len(listaMusicas)-1):
                for j in range(i+1, len(listaMusicas)-1):
                    if(listaMusicas[i]['Titulo'] == listaMusicas[j]['Titulo']):
                        listaMusicas[i]['Pontos'] = listaMusicas[i]['Pontos'] + listaMusicas[j]['Pontos']
                        listaMusicas.pop(j)

            listaMusicas = sorted(listaMusicas, key = lambda tup: (tup["Pontos"]))

            if(len(listaMusicas) < top): #Faz com que a query retorne apenas o numero de entradas pedido na variavel top
                top = len(listaMusicas)

            for i in range(top):
                outputList.append(listaMusicas[i])
            return arrumaStringRelevancia(outputList)

    #Retorna o top geral
    if(ano == None and artista == None):
        for i in range(len(topMusicas)-1,len(topMusicas) - 1 - top,-1):
            outputList.append(dados[topMusicas[i][0]])
        return arrumaStringRelevancia(outputList)

    #Retorna o top dos artistas em determinado ano
    if(artista != None and ano != None):
        #Faz o mesmo procedimento que a busca por artista
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            return sugestoesArtistas(indicesArtista)
        else:
            listaMusicas2 = []
            for i in indicesArtista:
                listaMusicas2.append(dados[i])

            listaMusicas = copy.deepcopy(listaMusicas2) #Faz uma copia de lista2 para lista, pq lista2 so referencia os registros de dados ao inves de criar eles novamente

            for i in range(len(listaMusicas)-1):
                for j in range(i+1, len(listaMusicas)-1):
                    if(listaMusicas[i]['Titulo'] == listaMusicas[j]['Titulo']):
                        listaMusicas[i]['Pontos'] = listaMusicas[i]['Pontos'] + listaMusicas[j]['Pontos']
                        listaMusicas.pop(j)

            listaMusicas = sorted(listaMusicas, key = lambda tup: (tup["Pontos"]))

            listaMusicasAno = [] #Lista com as musicas do artista no ano pedido

            for i in range(len(listaMusicas)):
                if(listaMusicas[i]['Ano'] == ano):
                    listaMusicasAno.append(listaMusicas[i])

            if(len(listaMusicasAno) < top):
                top = len(listaMusicasAno)
            if(len(listaMusicasAno) > 0):
                for i in range(top):
                    outputList.append(listaMusicasAno[i])
                return arrumaStringRelevancia(outputList)
            else:
                return "O artista não teve nenhuma música no top 200 da Billboard neste ano."


# Função utilizada para retirar a substring de Featuring com outro artista (caso tenha)
def retiraFeaturing(artistaString):

    if " Featuring" in artistaString:   # Se a música tiver um featuring, deve-se retirá-lo
            indexFeat = artistaString.find(" Featuring")   # pega índice do char space antes de Featuring
            artistaString = artistaString[:indexFeat]   # retorna apenas o primeiro artista

    return artistaString   # caso não caia no if, simplesmente retorna o artista assim como veio



# Query que retorna os N artistas mais relevantes de determinado ano
def relevanciaArtistaAno(dados, indiceFile, ano, maxArtistas, reversa):
    if(maxArtistas < 1):
        return "Você deve inserir um valor válido na quantidade de itens a ser retornado."

    achou = 0 #muda para 1 se o ano de entrada estiver no database
    # Loop que pega o ano passado para procurar no arquivo principal o artista mais relevante
    for entrada in range(len(indiceFile)):
        if indiceFile[entrada]['Ano'] == ano:
            index = entrada
            indexMin = indiceFile[index]['Min']
            indexMax = indiceFile[index]['Max']
            achou = 1

    if(achou == 0):
        return "O ano inserido não consta na base de dados."

    else:
        artistasDict = {}

        # Itera pelos indices daquele determinado ano construindo um dicionário de artistas e pontos acumulados
        while indexMin <= indexMax:

            artistaIterado = retiraFeaturing(dados[indexMin]['Artista'])
            if artistaIterado in artistasDict:
                artistasDict[artistaIterado] += dados[indexMin]['Pontos']
            else:
                artistasDict[artistaIterado] = dados[indexMin]['Pontos']

            indexMin += 1

        # a query será revertida caso o usuário peça
        dictSorted = sorted(artistasDict.items(), key=lambda kv: kv[1], reverse = not reversa)

        # pega os maxArtistas apenas da lista
        dictSorted = dictSorted[:maxArtistas]



        # Formatação da string final para ser posta na caixa de output

        # para concatenar na string de output como mais/menos relevantes
        if reversa:
            maisMenos = " menos "
        else:
            maisMenos = " mais "

        stringFinal = "Artistas" + maisMenos +  "relevantes de " + str(ano) + "\n\n"
        counter = 1

        # transforma numa string para poder ser inserida no output da text box
        for artista in dictSorted:
            stringFinal = stringFinal + str(counter) + ". " + artista[0] + " \n   Pontuação: " + str(artista[1]) + "\n\n"
            counter += 1

        return stringFinal



# Query que retorna os N artistas mais relevantes no geral
def topArtistasQuery(topArtistas, n, reversa):   # sendo n o número máximo de artistas

    if(n < 1):
        return "Você deve inserir um valor válido na quantidade de itens a ser retornado."

    if reversa:
        topArtistas = topArtistas[:-(n+1):-1]   # retorna os n últimos elementos em ordem reversa

    else:
        topArtistas = topArtistas[:n]

    # Formatação da string para output na tela
    stringFinal = "Artistas mais relevantes\n\n"
    counter = 1

    for artista in topArtistas:
        # counter serve para orientar posição do artista
        stringFinal = stringFinal + str(counter) + ". " + artista[0] + " \n   Pontuação: " + str(artista[1]) + "\n\n"
        counter += 1

    return stringFinal


#Retorna o artista mais popular e quantas semanas ele ficou na billboard
def comparaRelevArtista(trieArtistas, database, artista1, artista2):
    indicesArtista1 = findString(1, database, trieArtistas, artista1) #retorna os indices do arquivo principal com registros do artista
    indicesArtista2 = findString(1, database, trieArtistas, artista2) #retorna os indices do arquivo principal com registros do artista

    # tenta pegar strings formatadas dos artistas
    try:
        artista1 = retiraFeaturing(str(database[indicesArtista1[1][0]]['Artista']))
    except:
        pass

    try:
        artista2 = retiraFeaturing(str(database[indicesArtista2[1][0]]['Artista']))
    except:
        pass

    #variaveis com o numero de semanas que cada artista ficou na hot 100
    semanas1 = 0
    semanas2 = 0

    if (indicesArtista1[0] == False and indicesArtista2[0] == False): #testa se as duas entradas sao invalidas
        return "Nenhum artista foi encontrado.\nTente usar a opção de sugestão de artistas para receber sugestão de artistas que constam na base de dados."

    elif (indicesArtista1[0] == False or indicesArtista2[0] == False): #testa se achou os 2 artistas
        if indicesArtista1[0] == False: #se nao achou o primeiro devolve o segundo
            for i in indicesArtista2[1]:
                semanas2 += database[i]['Semanas'] #Adiciona o numero de semanas
            return(artista2, semanas2)
        else: #se nao achou o segundo devolve o primeiro
            for i in indicesArtista1[1]:
                semanas1 += database[i]['Semanas'] #Adiciona o numero de semanas
            return(artista1, semanas1)

    #compara os 2
    else:
        for i in indicesArtista1[1]:
            semanas1 += database[i]['Semanas'] #Adiciona o numero de semanas
        for i in indicesArtista2[1]:
            semanas2 += database[i]['Semanas'] #Adiciona o numero de semanas

        if(semanas1 > semanas2): #artista1 é mais relevante que o segundo
            return(artista1, semanas1)
        elif(semanas2 > semanas1): #artista2 é mais relevante que o primeiro
            return(artista2, semanas2)
        else: #trata o empate
            pontos1 = 0
            pontos2 = 0

            for i in indicesArtista1[1]:
                pontos1 += database[i]['Pontos'] #Adiciona o numero de semanas
            for i in indicesArtista2[1]:
                pontos2 += database[i]['Pontos'] #Adiciona o numero de semanas
            if (pontos1 > pontos2):
                return(artista1, semanas1)
            else:
                return(artista1, semanas1)


#Retorna a musica mais popular e quantas semanas ele ficou na billboard
def comparaRelevMusica(trieMusicas, trieArtistas, database, musica1, artista1, musica2, artista2):
    musica1Inds = findString(0, database, trieMusicas, musica1) #retorna os indices do arquivo principal com registros da musica
    musica2Inds = findString(0, database, trieMusicas, musica2) #retorna os indices do arquivo principal com registros da musica

    artista1 = findString(1, database, trieArtistas, artista1)
    artista2 = findString(1, database, trieArtistas, artista2)

    if artista1[0]:   # se o artista passado se encontra na trie
        artista1 = database[artista1[1][0]]['Artista']   # pega o nome do jeito que tá na base de dados

    # repete o mesmo processo para o artista 2
    if artista2[0]:
        artista2 = database[artista2[1][0]]['Artista']

    achou = 0 #se for 0 retorna que nao encontrou

    #------------------------------------------------------------------------------
    #Testa se alguma das musicas nao é valida
    #------------------------------------------------------------------------------
    if (musica1Inds[0] == False and musica2Inds[0] == False): #testa se as 2 entradas sao invalidas
        return None

    elif (musica1Inds[0] == False or musica2Inds[0] == False): #testa se achou os 2 artistas
        if musica1Inds[0] == False: #se nao achou o primeiro devolve o segundo
            for x in musica2Inds[1]:
                if (database[x]['Artista'] == artista2):
                    achou = 1
                    return(database[x]['Titulo'], database[x]['Semanas'])
        else: #se nao achou o segundo devolve o primeiro
            for x in musica1Inds[1]:
                if (database[x]['Artista'] == artista1):
                    achou = 1
                    return(database[x]['Titulo'], database[x]['Semanas'])

    #as 2 musicas sao validas
    else:
        for x in musica1Inds[1]:
                if (database[x]['Artista'] == artista1):
                    achou = 1
                    semanas1 = database[x]['Semanas']
                    indice1 = x
        for x in musica2Inds[1]:
                if (database[x]['Artista'] == artista2):
                    achou = 1
                    semanas2 = database[x]['Semanas']
                    indice2 = x

        if(semanas1 > semanas2):
            return(database[musica1Inds[1][0]]['Titulo'], semanas1)
        elif(semanas2 > semanas1):
            return(database[musica2Inds[1][0]]['Titulo'], semanas2)
        else: #mesmo numero de semanas
            if(database[indice1]['Pontos'] > database[indice2]['Pontos']):
                return(database[musica1Inds[1][0]]['Titulo'], semanas1)
            else:
                return(database[musica2Inds[1][0]]['Titulo'], semanas2)



# Query que dado um artista, lista as músicas deste artista ou retorna uma sugestão de artistas caso o passado não for encontrados
def listaMusicasArtista(database, trieArtistas, artista):

    # procura artista na trie de artistaString
    indicesArtista = findString(1, database, trieArtistas, artista)

    if not indicesArtista[0]:   # se não encontrar o artista, retorna as sugestões de artistas
        return "Artista não encontrado. Sugestões:\n" + outputSugestoesLista(indicesArtista[1])

    musicas = []   # lista que vai gravar as músicas daquele dado artista

    for indice in indicesArtista[1]:
        musica = database[indice]['Titulo'] + " - Ano: " + str(database[indice]['Ano'])
        if not(musica in musicas):   # se a musica já não constar na lista de músicas, insere na lista
            musicas.append(musica)

    return "Músicas:\n" + outputSugestoesLista(musicas)
