#!/usr/bin/python3
# -*- coding: utf-8 -*-

import io
import os
import sys

import numpy as np
from botocore.exceptions import ClientError

import consulta

FICHERO = os.path.join(os.getcwd(), "Files", "NodosJuegos.csv")


def leer_juegos(ruta):
    juegos = {}
    with open(ruta, "r") as reader:
        reader.readline()
        for line in reader:
            partes = [campo.strip() for campo in line.split(",")]
            if len(partes) < 5 or partes[0] == "":
                continue
            nombre = partes[1]
            if nombre == "":
                continue
            juegos[partes[0]] = {
                "nombre": nombre,
                "texto": consulta.texto_catalogo(nombre, partes[2], partes[3], partes[4]),
            }
    return list(juegos.values())


def subir(juegos):
    nombres = np.asarray([juego["nombre"] for juego in juegos])
    vectores = consulta.embeber_lote([juego["texto"] for juego in juegos])
    buffer = io.BytesIO()
    np.savez_compressed(buffer, vectores=vectores, nombres=nombres)
    consulta.cliente().put_object(
        Bucket=consulta.BUCKET,
        Key=consulta.CLAVE,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream",
    )


def main():
    if not os.path.exists(FICHERO):
        print("Error: No existe Files/NodosJuegos.csv")
        return 1
    juegos = leer_juegos(FICHERO)
    if len(juegos) == 0:
        print("Error: El catálogo no tiene juegos")
        return 1
    print("Juegos únicos: %s" % len(juegos))
    try:
        subir(juegos)
    except ClientError as error:
        print("Error: %s" % error, file=sys.stderr)
        return 1
    print("Fin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
