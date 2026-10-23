#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import time
import xml.etree.ElementTree as ET

# Tratamos los usuarios
def leerUsuarios(fichero):

    # Abrimos el fichero con los usuarios a tratar
    with open(fichero, 'r') as reader:
        # Ignoramos la cabecera
        reader.readline()
        nombreUsuarios = []
        for line in reader:
            partido = line.split(',')
            nombreUsuarios.append(partido[0])

    i = 1
    longitud = len(nombreUsuarios)
    with open(ficheroDestinoNodosJuegos, "a") as ficheroNodos:
        with open(ficheroDestinoAristasJuegos, "a") as ficheroAristas:
            for nombreUsuario in nombreUsuarios:
                try:
                    print(str(i)+'/' + str(longitud) + ' '+str(nombreUsuario))
                    obtenerDatosUsuario(nombreUsuario, ficheroNodos, True)
                    i += 1

                    calcularAristas(ficheroAristas)
                except:
                    tratarUsuarioError(True, nombreUsuario)


# Volvemos a tratar los usuarios que fallaron
def leerUsuariosError():
    with open(ficheroDestinoNodosJuegos, "a") as ficheroNodos:
        with open(ficheroDestinoAristasJuegos, "a") as ficheroAristas:
            for nombreUsuario in usersError:
                try:
                    obtenerDatosUsuario(nombreUsuario, ficheroNodos, False)
                    calcularAristas(ficheroAristas)
                except:
                    tratarUsuarioError(False, nombreUsuario)


# Obtenemos los datos de los juegos valorados por el usuario
# recibido como parámetro
def obtenerDatosUsuario(user, ficheroNodos, TratarErrores):

    response = requests.get(
        "https://www.boardgamegeek.com/xmlapi/collection/%(usr)s?rated=1" % {'usr': user})

    # Si recibimos una respuesta 202 tenemos que esperar a que la api genere
    # los datos del usuario pedido, tenemos que volver a realizar la petición
    # pasados X segundos
    while response.status_code == 202:
        time.sleep(segundosEspera)
        response = requests.get(
            "https://www.boardgamegeek.com/xmlapi/collection/%(usr)s?rated=1" % {'usr': user})

    # xml = response.text.replace('\t', ' ')

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text.strip())

            if root.tag != 'errors':
                # Obtenemos los nombres y los ids de los juegos valorados
                for child in root:
                    idJuego = child.attrib['objectid']

                    # Añadimos el juego y su nota a la lista
                    for datosJuego in child:
                        if datosJuego.tag == 'stats':
                            for estadisticas in datosJuego:
                                if estadisticas.tag == 'rating':
                                    nota = estadisticas.attrib['value']
                                    valores_Juegos[idJuego] = float(nota)

                    nombreJuego = ''
                    yearJuego = -1
                    minplayers = -1
                    maxplayers = -1
                    minplaytime = -1
                    maxplaytime = -1
                    playingtime = -1
                    numowned = -1
                    age = -1

                    for datosJuego in child:

                        # Nombre
                        if datosJuego.tag == 'name':
                            nombreJuego = (datosJuego.text).replace(',', ';')

                        # Año publicación
                        if datosJuego.tag == 'yearpublished':
                            yearJuego = datosJuego.text

                        # Estadisticas
                        if datosJuego.tag == 'stats':
                            # Los juegos nos siempre tienen las mismas estdisticas
                            for atributo in datosJuego.attrib:
                                if atributo == 'minplayers':
                                    minplayers = datosJuego.attrib['minplayers']
                                if atributo == 'maxplayers':
                                    maxplayers = datosJuego.attrib['maxplayers']
                                if atributo == 'minplaytime':
                                    minplaytime = datosJuego.attrib['minplaytime']
                                if atributo == 'maxplaytime':
                                    maxplaytime = datosJuego.attrib['maxplaytime']
                                if atributo == 'playingtime':
                                    playingtime = datosJuego.attrib['playingtime']
                                if atributo == 'numowned':
                                    numowned = datosJuego.attrib['numowned']
                                if atributo == 'age':
                                    age = datosJuego.attrib['age']

                    juegos_Tratados[idJuego] = nombreJuego
                    juego = []
                    juego.append(idJuego)
                    juego.append(nombreJuego)
                    juego.append(yearJuego)
                    juego.append(minplayers)
                    juego.append(maxplayers)
                    juego.append(minplaytime)
                    juego.append(maxplaytime)
                    juego.append(playingtime)
                    juego.append(numowned)
                    juego.append(age)

                    guardarNodoFichero(ficheroNodos, juego)
            else:
                tratarUsuarioError(TratarErrores, user)
        except Exception:
            print('Datos mal formados')

    else:
        tratarUsuarioError(TratarErrores, user)


# Cuando un usuario falla al obtener los datos los encolamos para tratarlos aparte
def tratarUsuarioError(TratarErrores, user):
    if TratarErrores:
        usersError.append(user)
    else:
        with open(ficheroUsuariosError, "a") as fichero:
            fichero.write(str(user)+'\n')


# Guardamos un nodo en el fichero de resultados
def guardarNodoFichero(fichero, juego):
    for dato in juego:
        fichero.write(str(dato).strip() + ', ')
    fichero.write('\n')


# Calculamos los juegos relacionados entre sí para cada usuario
# Dos juegos estarán relacionados siempre que un mismo usuario
# los haya valorado con una nota superior o igual a una variable
def calcularAristas(ficheroAristas):
    while len(valores_Juegos) != 0:
        juego1, valor1 = valores_Juegos.popitem()

        if valor1 >= valorParaArista:
            for juego2, valor2 in valores_Juegos.items():
                if valor2 >= valorParaArista:
                    if juego1 != juego2:
                        # Creamos el identificador de la arista
                        clave = ''
                        if(int(juego1) < int(juego2)):
                            clave = juego1+'-'+juego2
                        else:
                            clave = juego2+'-'+juego1

                        ficheroAristas.write(clave+'\n')


# Gestión de los ficheros que se usan
def configurarFicheros():
    result = True

    # Aseguramos que exista la carpeta para guardar los ficheros
    if not os.path.exists(os.path.join(os.getcwd(), carpetaFicheros)):
        os.makedirs(os.path.join(os.getcwd(), carpetaFicheros))

    # Creamos el fichero para guardar los nodos
    # Creamos la cabecera del fichero
    with open(ficheroDestinoNodosJuegos, 'w') as nodos_Juegos:
        nodos_Juegos.write(
            'Id, Name, Year, MinPlayers, MaxPlayers, MinPlayTime, MaxPlayTime, PlayingTime, NumOwned, Age,' + '\n')

    # Creamos el fichero para guardar las aristas
    # Creamos la cabecera del fichero
    with open(ficheroDestinoAristasJuegos, 'w') as aristas_Juegos:
        aristas_Juegos.write('Relacion' + '\n')

    # Creamos el fichero para guardar los usuarios que han dado error
    if not os.path.exists(ficheroUsuariosError):
        with open(ficheroUsuariosError, 'w') as usuarios_Error:
            usuarios_Error.write('UsuariosFallidos' + '\n')

    # Comprobamos que exista el fichero para leer los usuarios
    if not os.path.exists(os.path.join(os.getcwd(), ficheroOrigenUsarios)):
        result = False

    return result


def retryUsuarios(fichero):
    # Abrimos el fichero con los usuarios a tratar
    with open(fichero, 'r') as reader:
        # Ignoramos la cabecera
        reader.readline()
        nombreUsuarios = []
        for line in reader:
            nombreUsuarios.append(line.strip())

    i = 1
    longitud = len(nombreUsuarios)
    siguenError = []

    with open(ficheroDestinoNodosJuegos, "a") as ficheroNodos:
        with open(ficheroDestinoAristasJuegos, "a") as ficheroAristas:
            for nombreUsuario in nombreUsuarios:
                try:
                    print(str(i)+'/' + str(longitud) + ' '+str(nombreUsuario))
                    obtenerDatosUsuario(nombreUsuario, ficheroNodos, True)
                    i += 1

                    calcularAristas(ficheroAristas)
                except:
                    siguenError.append(nombreUsuario)

    with open(ficheroUsuariosError, 'w') as usuarios_Error:
        usuarios_Error.write('UsuariosFallidos' + '\n')

    for elemento in siguenError:
        tratarUsuarioError(False, elemento)


# Main
def main():

    # Obtenemos los parámetros de entrada
    if len(sys.argv) == 1:  # Sin parametros -> ejecución por defecto
        # Leemos los usuarios del fichero de origen
        leerUsuarios(ficheroOrigenUsarios)

        # Reintentamos los usuarios que han dado error
        leerUsuariosError()

    elif len(sys.argv) == 2:
        if sys.argv[1] == '--errores':  # Ejecución para tratar errores
            retryUsuarios(ficheroUsuariosError)


if __name__ == '__main__':
    # Variables
    usersError = []

    juegos_Tratados = dict()
    valores_Juegos = dict()
    # Variables

    # Configuración
    valorParaArista = 9.0
    segundosEspera = 5

    carpetaFicheros = 'Files'

    ficheroOrigenUsarios = os.path.join(
        os.getcwd(), carpetaFicheros, 'usuarios.csv')
    ficheroUsuariosError = os.path.join(
        os.getcwd(), carpetaFicheros, 'usuariosError.csv')

    ficheroDestinoNodosJuegos = os.path.join(
        os.getcwd(), carpetaFicheros, 'NodosJuegos.csv')
    ficheroDestinoAristasJuegos = os.path.join(
        os.getcwd(), carpetaFicheros, 'AristasJuegos.csv')

    correcto = configurarFicheros()
    # Configuración

    if correcto:
        main()
    else:
        print('Error: No existe fichero de entrada con los usuarios')

    print('Fin')
