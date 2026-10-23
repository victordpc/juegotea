#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import time
import xml.etree.ElementTree as ET


def main():
    usuarios = dict()

    for juego in juegosOrigen:
        pagina = 1
        continuar = True

        while continuar:
            response = sesion.get(
                "https://api.geekdo.com/xmlapi2/thing?id=%(juego)s&comments=1&page=%(pagina)s&pagesize=100" % {'juego': juego, 'pagina': pagina},
                timeout=30)

            if response.status_code != 200:
                print("Error API %s" % response.status_code)
                if response.status_code == 401:
                    print("Hace falta la variable BGG_TOKEN")
                return False

            root = ET.fromstring(response.text)

            if root.tag != 'errors':
                for nodo in root[0]:
                    if (nodo.tag == 'name'):
                        if (nodo.attrib['type'] == 'primary'):
                            print('Juego '+nodo.attrib['value'] + ' pagina: ' + str(pagina))
                    if nodo.tag == 'comments':
                        numeroComentarios = nodo.attrib['totalitems']
                        if pagina*100 >= int(numeroComentarios):
                            continuar = False

                        for comentario in nodo:
                            if comentario.attrib['rating'] != 'N/A':
                                nombre = comentario.attrib['username']
                                usuarios[nombre] = 0

            pagina += 1
    guardarUsuarios(usuarios)
    return True


# Gestión de los ficheros que se usan
def configurarFicheros():
    # Aseguramos que exista la carpeta para guardar los ficheros
    if not os.path.exists(os.path.join(os.getcwd(), carpetaFicheros)):
        os.makedirs(os.path.join(os.getcwd(), carpetaFicheros))

    # Creamos el fichero para guardar los nodos
    # Creamos la cabecera del fichero
    return True


def guardarUsuarios(usuarios):
    with open(ficheroUsarios, 'w') as fichero:
        fichero.write('Usr,' + '\n')
        for usuario in usuarios.keys():
            fichero.write(usuario + ',\n')


if __name__ == '__main__':
    # Variables
    # catan azul gloomhaven terraforming-mars scythe rising-sun
    # juegosOrigen = ['13', '230802', '174430', '167791', '169786', '205896']
    juegosOrigen = ['230802']
    # Variables
    # Configuración
    carpetaFicheros = 'Files'
    ficheroUsarios = os.path.join(os.getcwd(), carpetaFicheros, 'usuarios.csv')
    configurarFicheros()
    sesion = requests.Session()
    token = os.environ.get("BGG_TOKEN", "").strip()
    if token:
        sesion.headers["Authorization"] = "Bearer " + token
    # Configuración

    if not main():
        sys.exit(1)

    print('Fin')
