import pandas as pd
import xlrd
import pickle #modulo usado para serializar dados para o arquivo binario
import os
import time
import copy
from unicodedata import normalize




'''''''''''''''

Definição das Querys

'''''''''''''''

# Query que retorna um numero N de pesquisas em ordem de relevancia, filtrando por artista/ano opcionalmente

def relevancia(dados, top, ano=None, artista=None):
    #Retornando de um determinado ano
    if(ano != None and artista == None):
        #Consultando do arquivo de indices qual o index inicial do ano que o usuario entrou
        comeco = -1 #Se estiver em -1 eh pq nao encontrou o ano
        for x in indices:
            if x['Ano'] == ano:
                comeco = x['Min']
        if(comeco != -1):
            for i in range(comeco, comeco+top):
                print(dados[i])
        else:
            print('O ano pesquisado não esta na base de dados')

    #Retornando de um determinado artista
    if(artista != None and ano == None):
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            print('Artista não encontrado')
            print('Sugestões de artistas:')
            print(indicesArtista)
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
                print(listaMusicas[i])

    #Retorna o top geral
    if(ano == None and artista == None):
        for i in range(top):
            print(dados[topMusicas[i][0]])

    #Retorna o top dos artistas em determinado ano
    if(artista != None and ano != None):
        #Faz o mesmo procedimento que a busca por artista
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            print('Artista não encontrado')
            print('Sugestões de artistas:')
            print(indicesArtista)
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
                    print(listaMusicasAno[i])
            else:
                print("Esse artista não teve nenhuma música no top 200 da billboard nesse ano")



def relevanciaReversa(dados, top, ano=None, artista=None):
    #Retornando de um determinado ano
    if(ano != None and artista == None):
        #Consultando do arquivo de indices qual o index inicial do ano que o usuario entrou
        comeco = -1 #Se estiver em -1 eh pq nao encontrou o ano
        for x in indices:
            if x['Ano'] == ano:
                comeco = x['Max']
        if(comeco != -1):
            for i in range(comeco, comeco-top, -1): #(start,stop,step)
                print(dados[i])
        else:
            print('O ano pesquisado não esta na base de dados')

    #Retornando de um determinado artista
    if(artista != None and ano == None):
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            print('Artista não encontrado')
            print('Sugestões de artistas:')
            print(indicesArtista)
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
                print(listaMusicas[i])

    #Retorna o top geral
    if(ano == None and artista == None):
        for i in range(len(topMusicas)-1,len(topMusicas) - 1 - top,-1):
            print(dados[topMusicas[i][0]])

    #Retorna o top dos artistas em determinado ano
    if(artista != None and ano != None):
        #Faz o mesmo procedimento que a busca por artista
        indicesArtista = findString(1, dados, trieArtistas, artista)[1] #retorna os indices do arquivo principal com registros do artista
        if(type(indicesArtista[0]) == str):
            print('Artista não encontrado')
            print('Sugestões de artistas:')
            print(indicesArtista)
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
                    print(listaMusicasAno[i])
            else:
                print("Esse artista não teve nenhuma música no top 200 da billboard nesse ano")


# Função utilizada para retirar a substring de Featuring com outro artista (caso tenha)
def retiraFeaturing(artistaString):

    if " Featuring" in artistaString:   # Se a música tiver um featuring, deve-se retirá-lo
            indexFeat = artistaString.find(" Featuring")   # pega índice do char space antes de Featuring
            artistaString = artistaString[:indexFeat]   # retorna apenas o primeiro artista

    return artistaString   # caso não caia no if, simplesmente retorna o artista assim como veio



# Query que retorna os N artistas mais relevantes de determinado ano
def relevanciaArtistaAno(dados, indiceFile, ano, maxArtistas, reversa):
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
def comparaRelevArtista(artista1, artista2):
    indicesArtista1 = findString(1, database, trieArtistas, artista1) #retorna os indices do arquivo principal com registros do artista
    indicesArtista2 = findString(1, database, trieArtistas, artista2) #retorna os indices do arquivo principal com registros do artista

    #variaveis com o numero de semanas que cada artista ficou na hot 100
    semanas1 = 0
    semanas2 = 0

    if (indicesArtista1[0] == False and indicesArtista2[0] == False): #testa se as duas entradas sao invalidas
        return None

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
def comparaRelevMusica(musica1, artista1, musica2, artista2):
    musica1Inds = findString(1, database, trieMusicas, musica1) #retorna os indices do arquivo principal com registros da musica
    musica2Inds = findString(1, database, trieMusicas, musica2) #retorna os indices do arquivo principal com registros da musica

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
                    return(musica2, database[x]['Semanas'])
        else: #se nao achou o segundo devolve o primeiro
            for x in musica1Inds[1]:
                if (database[x]['Artista'] == artista1):
                    achou = 1
                    return(musica1, database[x]['Semanas'])

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
            return(musica1, semanas1)
        elif(semanas2 > semanas1):
            return(musica2, semanas2)
        else: #mesmo numero de semanas
            if(database[indice1]['Pontos'] > database[indice2]['Pontos']):
                return(musica1, semanas1)
            else:
                return(musica2, semanas2)
