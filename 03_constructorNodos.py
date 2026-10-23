#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys


def configurarFicheros():
    result = True

    if not os.path.exists(os.path.join(os.getcwd(), carpetaFicheros)):
        result = False
    elif not os.path.exists(os.path.join(os.getcwd(), ficheroNodos)):
        result = False

    with open(ficheroConstruidoNodos, 'w') as nodos_Juegos:
        nodos_Juegos.write(
            'Id, Name, Year, MinPlayers, MaxPlayers, MinPlayTime, MaxPlayTime, PlayingTime, NumOwned, Age,' + '\n')

    return result

# Guarda las aristas en un fichero
def escribirNodos(aristas):
    with open(ficheroConstruidoNodos, "a") as fichero:
        for juego in aristas.values():
            fichero.write(juego)


def leerEntrada():
    datos = dict()
    with open(ficheroNodos, "r") as fichero:
        fichero.readline()

        # 217554, Dr. Microbe, 2017, 2, 4, 15, 15, 15, 381, -
        for linea in fichero:
            juego = linea.split(',')[0]
            datos[int(juego)] = linea
    return datos


def main():

    # Leemos el fichero de entrada con los datos en bruto
    datos = leerEntrada()

    # Guardamos el resultado de la recomendación
    escribirNodos(datos)

    print('Fin')


if __name__ == '__main__':
    tipoAristas = 'undirected'

    # Configuración
    carpetaFicheros = 'Files'
    ficheroNodos = os.path.join(
        os.getcwd(), carpetaFicheros, 'NodosJuegos.csv')
    ficheroConstruidoNodos = os.path.join(
        os.getcwd(), carpetaFicheros, 'NodosGrafo.csv')

    correcto = configurarFicheros()
    # Configuración

    if correcto:
        main()
    else:
        print('Error: No existen ficheros con datos de entrada')
