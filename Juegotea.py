#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from botocore.exceptions import ClientError

import consulta


def mensajeSalida(resultado, encontrados):
    msg = '\n'

    if len(encontrados) > 0 and len(resultado) > 0:
        msg += 'Las recomendaciones para '

        if len(encontrados) == 1:
            msg += 'el juego: '
        else:
            msg += 'los juegos: '

        for juego in encontrados:
            msg += juego + ', '
        msg = msg[:-2]

        if len(resultado) == 1:
            msg += ' es'
        else:
            msg += ' son: '

        for juego in resultado:
            msg += juego["nombre"] + ', '
        msg = msg[:-2]

    else:
        msg += 'No se ha encontrado información para ninguno de los juegos introducidos'

    return msg


def mensajeAyuda():
    msg = 'Recomendador Juegotea\n\n'
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

    if len(sys.argv) > 1:
        for argumento in sys.argv:
            entrada.append(argumento)
        entrada.remove(entrada[0])
        if entrada[0] == '-h':
            continuar = False
            msg = mensajeAyuda()
    else:
        error = True
        msg = 'No se proporcionan argumentos de entrada'

    if (not error) and continuar:
        try:
            resultado, encontrados, _ = consulta.recomendar(entrada)
            msg = mensajeSalida(resultado, encontrados)
        except ClientError as fallo:
            error = True
            msg = 'Error: %s' % fallo

    if error:
        if len(msg) > 0:
            print(msg)
        print('Para consultar la ayuda ejecute con la opción -h')
        return 1

    print(msg)
    return 0


if __name__ == '__main__':
    sys.exit(main())
