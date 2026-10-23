#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import networkx as nx

# Gestión de los ficheros que se usan
def configurarFicheros():
    result = True

    if not os.path.exists(os.path.join(os.getcwd(), carpetaFicheros)):
        result = False
    elif not os.path.exists(os.path.join(os.getcwd(), ficheroAristas)):
        result = False

    # Creamos el fichero para guardar las recomendaciones
    # Creamos la cabecera del fichero
    with open(ficheroRecomendador, 'w') as aristas_Juegos:
        msg = 'Juego,'
        i = 1

        while i <= respuestas:
            msg += 'R'+str(i)+', P'+str(i)+', '
            i += 1
        msg = msg[:-2]
        msg += '\n'

        aristas_Juegos.write(msg)
    return result


def montarGrafo(grafo):

    # Para los calculos a realizar podemos generar
    # el grafo con la información de las aristas

    # Cargamos las aristas
    cargarAristas(grafo)


def cargarAristas(grafo):
    with open(ficheroAristas, 'r') as reader:
        # Leemos la cabecera
        reader.readline()

        for line in reader:
            arista = line.split(',')
            grafo.add_edge(int(arista[0].strip()),
                           int(arista[1].strip()), weight=float(arista[2].strip()))


def recomendadorEW(grafo):
    # Diccionario con los pesos de los juegos relacionados con la entrada
    resultado = dict()
    j = 0
    aristas = grafo.number_of_edges()
    total = grafo.number_of_nodes()

    print('Total aristas grafo: '+str(aristas) +
          ' Total nodos grafo: ' + str(total))

    for juego in grafo.nodes():
        j += 1
        print(str(j)+' / '+str(total))

        salida = dict()
        resultado[juego] = []
        # Consultamos para cada juego sus vecinos
        consultarVecinosJuego(grafo, juego, salida)

        if len(salida) > 0:
            # Ordenamos los resultados
            # Obtenemos los X juegos con mayor valoración
            salidaOrdenada = sorted(salida.keys(), key=lambda x: salida[x])

            i = 0
            while i < respuestas and i < len(salidaOrdenada):
                elegido = salidaOrdenada.pop()
                (resultado[juego]).append(elegido)
                (resultado[juego]).append(salida[elegido])
                i += 1

    return resultado


def consultarVecinosJuego(grafo, id, salida):
    vecinos = grafo.neighbors(id)

    # Devolvemos sus vecinos
    for vecino in vecinos:
        peso = (grafo.get_edge_data(id, vecino))['weight']
        valor = salida.get(vecino, 0)
        salida[vecino] = peso + valor


def guardarDatos(datos):
    with open(ficheroRecomendador, "a") as fichero:
        for Juego, Recomendaciones in datos.items():
            fichero.write(str(Juego)+', ')
            for dato in Recomendaciones:
                fichero.write(str(dato)+', ')
            fichero.write('\n')


def main():

    # Creamos el grafo
    G = nx.Graph()

    # Montamos el grafo
    montarGrafo(G)

    # Ejecutamos el algoritmo de recomendación
    datos = dict()
    datos = recomendadorEW(G)

    # Guardamos el resultado de la recomendación
    guardarDatos(datos)

    print('Fin')


if __name__ == '__main__':
    msg = ''
    respuestas = 10
    # Configuración
    carpetaFicheros = 'Files'
    ficheroAristas = os.path.join(
        os.getcwd(), carpetaFicheros, 'AristasGrafo.csv')
    ficheroRecomendador = os.path.join(
        os.getcwd(), carpetaFicheros, 'Recomendaciones.csv')

    correcto = configurarFicheros()
    # Configuración

    if correcto:
        main()
    else:
        print('Error: No existen ficheros con datos de entrada')
