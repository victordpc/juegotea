#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from collections import defaultdict

import boto3
from botocore.exceptions import ClientError

import consulta

VECINOS = 20
NODOS = os.path.join(os.getcwd(), "Files", "NodosJuegos.csv")
ARISTAS = os.path.join(os.getcwd(), "Files", "AristasJuegos.csv")


def leer_nodos(ruta):
    juegos = {}
    with open(ruta, "r") as reader:
        reader.readline()
        for line in reader:
            partes = [campo.strip() for campo in line.split(",")]
            if len(partes) < 3 or partes[0] == "" or partes[1] == "":
                continue
            juegos[partes[0]] = {
                "nombre": partes[1].replace(";", ","),
                "anio": partes[2],
            }
    return juegos


def contar_pares(ruta):
    pesos = defaultdict(int)
    with open(ruta, "r") as reader:
        for line in reader:
            clave = line.strip()
            if "-" not in clave:
                continue
            pesos[clave] += 1
    return pesos


def vecinos_de(pesos):
    vecinos = defaultdict(list)
    for clave, peso in pesos.items():
        juego1, juego2 = clave.split("-", 1)
        vecinos[juego1].append((juego2, peso))
        vecinos[juego2].append((juego1, peso))
    return vecinos


def construir(nodos, vecinos):
    tabla = {}
    for origen, candidatos in vecinos.items():
        juego = nodos.get(origen)
        if juego is None or juego["nombre"] == "":
            continue
        ordenados = sorted(candidatos, key=lambda par: par[1], reverse=True)[:VECINOS]
        lista = []
        for destino, peso in ordenados:
            otro = nodos.get(destino)
            if otro is None or otro["nombre"] == "":
                continue
            lista.append({
                "nombre": otro["nombre"],
                "anio": otro["anio"],
                "peso": peso,
            })
        if len(lista) == 0:
            continue
        tabla[juego["nombre"].casefold()] = lista
    return tabla


def subir(tabla):
    cuerpo = json.dumps(tabla, ensure_ascii=False).encode("utf-8")
    consulta.cliente().put_object(
        Bucket=consulta.BUCKET,
        Key=consulta.CLAVE,
        Body=cuerpo,
        ContentType="application/json",
    )
    return len(cuerpo)


def main():
    if not os.path.exists(NODOS) or not os.path.exists(ARISTAS):
        print("Error: faltan NodosJuegos.csv o AristasJuegos.csv")
        return 1
    try:
        nodos = leer_nodos(NODOS)
        tabla = construir(nodos, vecinos_de(contar_pares(ARISTAS)))
        tamano = subir(tabla)
    except ClientError as fallo:
        print("Error: %s" % fallo)
        return 1
    print("Juegos %s" % len(tabla))
    print("Bytes %s" % tamano)
    print("Fin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
