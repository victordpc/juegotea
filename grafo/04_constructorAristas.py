#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys


def configurarFicheros():
    result = True

    if not os.path.exists(os.path.join(os.getcwd(), carpetaFicheros)):
        result = False
    elif not os.path.exists(os.path.join(os.getcwd(), ficheroAristas)):
        result = False

    with open(ficheroConstruidoAristsas, 'w') as aristas_Juegos:
        aristas_Juegos.write('Source, Target, Weight, Type' + '\n')

    return result

# Guarda las aristas en un fichero
def escribirAristas(aristas):
    with open(ficheroConstruidoAristsas, "a") as fichero:

        for arista, peso in aristas.items():
            partido = arista.split('-')
            origen = partido[0]
            destino = partido[1]

            fichero.write(str(origen)+', '+str(destino) + ', ' +
                          str(peso)+', ' + tipoAristas + '\n')


def leerEntrada():
    datos = dict()
    i = 0
    with open(ficheroAristas, "r") as fichero:
        fichero.readline()

        for linea in fichero:
            print(i)
            i += 1
            valorClave = datos.get(linea.strip(), 0)
            datos[linea.strip()] = valorClave + 1

    return datos


def main():

    # Leemos el fichero de entrada con los datos en bruto
    datos = leerEntrada()

    # Guardamos el resultado de la recomendación
    escribirAristas(datos)

    print('Fin')


if __name__ == '__main__':
    tipoAristas = 'undirected'

    # Configuración
    carpetaFicheros = 'Files'
    ficheroAristas = os.path.join(
        os.getcwd(), carpetaFicheros, 'AristasJuegos.csv')
    ficheroConstruidoAristsas = os.path.join(
        os.getcwd(), carpetaFicheros, 'AristasGrafo.csv')

    correcto = configurarFicheros()
    # Configuración

    if correcto:
        main()
    else:
        print('Error: No existen ficheros con datos de entrada')
