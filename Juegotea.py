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
    elif not os.path.exists(os.path.join(os.getcwd(), ficheroNodos)):
        result = False
    elif not os.path.exists(os.path.join(os.getcwd(), ficheroRecomendador)):
        result = False

    return result


def cargarJuegos():
    juegoId = dict()
    idJuego = dict()

    with open(ficheroNodos, 'r') as reader:
        # Leemos la cabecera
        reader.readline()

        for line in reader:
            juego = line.split(',')
            juegoId[juego[1].strip().upper()] = int(juego[0].strip())
            idJuego[int(juego[0].strip())] = juego[1].strip()

    return juegoId, idJuego


def cargarRecomendaciones():
    resultado = dict()

    with open(ficheroRecomendador, 'r') as reader:
        # Leemos la cabecera
        reader.readline()

        for line in reader:
            juego = line.strip().split(',')

            elemento = int(juego[0].strip())
            resultado[elemento] = []

            for i in range(len(juego)):
                if (i > 0) & (juego[i].strip() != ''):
                    if i % 2 == 1:
                        (resultado[elemento]).append(int(juego[i].strip()))
                    else:
                        (resultado[elemento]).append(float(juego[i].strip()))

    return resultado


def recomendador(recomendaciones, juegoId, idJuego, entrada):
    # Diccionario con los pesos de los juegos relacionados con la entrada
    salida = dict()
    resultado = []
    encontrados = []
    noEncontrados = []

    for juego in entrada:

        # Encontramos el juego pedido
        if juegoId.get(juego.upper(), -1) != -1:
            id = juegoId[juego.upper()]
            encontrados.append(id)
            # Consultamos para cada juego sus recomendaciones
            consultarRecomendaciones(recomendaciones, id, salida)
        else:
            noEncontrados.append(juego)

    # Eliminamos de la lista las posibles ocurrencias de los juegos de entrada
    for juego in encontrados:
        salida.pop(juego, 0)

    if len(salida) > 0:
        # Ordenamos los resultados
        # Obtenemos los X juegos con mayor valoración
        salidaOrdenada = sorted(salida.keys(), key=lambda x: salida[x])

        i = 0
        while i < respuestas:
            elegido = salidaOrdenada.pop()
            resultado.append(idJuego[elegido])
            i += 1

    return resultado, encontrados, noEncontrados


def consultarRecomendaciones(recomendaciones, id, salida):
    vecinos = recomendaciones[id]

    # Devolvemos sus vecinos
    for j in range(int(len(vecinos)/2)):
        idRecomendado = j*2
        idPeso = j*2+1
        valorAcumulado = salida.get(vecinos[idRecomendado], 0)
        peso = vecinos[idPeso]
        salida[vecinos[idRecomendado]] = peso + valorAcumulado


def mensajeSalida(resultado, encontrados, noEncontrados, idJuego):
    msg = '\n'

    if len(encontrados) > 0 and len(resultado) > 0:
        msg += 'Las recomendaciones para '

        if len(encontrados) == 1:
            msg += 'el juego: '
        else:
            msg += 'los juegos: '

        for juego in encontrados:
            msg += idJuego[juego]+', '
        msg = msg[:-2]

        if len(resultado) == 1:
            msg += ' es'
        else:
            msg += ' son: '

        for juego in resultado:
            msg += juego+', '
        msg = msg[:-2]

        if len(noEncontrados) > 0:
            msg += '\n\nNo se ha encontrado información para '

            if len(noEncontrados) == 1:
                msg += 'el juego: '
            else:
                msg += 'los juegos: '

            for juego in noEncontrados:
                msg += juego+', '
            msg = msg[:-2]

    else:
        msg += 'No se ha encontrado información para ninguno de los juegos introducidos'

    return msg


def mensajeAyuda():
    msg = 'Recomendador Juegotea, un recomendador basado en grafos\n\n'
    msg += 'Usage: juegotea [arg ...]|[-h]\n'
    msg += '\n'
    msg += '    Introducir los nombres de los juegos separados por un único'
    msg += ' caracter de espacio, en caso de querer introducir un nombre'
    msg += ' compuesto por varias palabras introducirlo entre comillas\n'
    msg += '    Example: Juegotea Juego1, "Juego 2"\n'
    msg += '\n'
    msg += '    Commands:\n'
    msg += '      -h    - Muestra la ayuda\n'
    return msg


def main():
    entrada = []
    error = False
    continuar = True
    msg = ''

    # Obtenemos los parámetros de entrada
    if len(sys.argv) > 1:
        for argumento in sys.argv:
            entrada.append(argumento)
        entrada.remove(entrada[0])
        # Controlamos si quieren mostrar la ayuda
        if entrada[0] == '-h':
            continuar = False
            msg = mensajeAyuda()
    else:
        error = True
        msg = 'No se proporcionan argumentos de entrada'

    if (not error) & continuar:
        # Cargamos las recomendaciones calculadas
        recomendaciones = dict()
        recomendaciones = cargarRecomendaciones()

        # Cargamos los juegos
        juegoId = dict()
        idJuego = dict()
        juegoId, idJuego = cargarJuegos()

        # Encontramos los juegos
        resultado, encontrados, noEncontrados = recomendador(
            recomendaciones, juegoId, idJuego, entrada)

        # Montamos el mensaje de salida
        msg = mensajeSalida(resultado, encontrados, noEncontrados, idJuego)

    # Si se ha producido un error lo mostramos por pantalla
    if error:
        if len(msg) > 0:
            print(msg)
        print('Para consultar la ayuda ejecute con la opción -h')
    else:
        print(msg)


if __name__ == '__main__':
    msg = ''
    respuestas = 5
    # Configuración
    carpetaFicheros = 'Files'
    ficheroNodos = os.path.join(
        os.getcwd(), carpetaFicheros, 'NodosJuegos.csv')
    ficheroRecomendador = os.path.join(
        os.getcwd(), carpetaFicheros, 'Recomendaciones.csv')

    correcto = configurarFicheros()
    # Configuración

    if correcto:
        main()
    else:
        print('Error: No existen ficheros con datos de entrada')
