#!/usr/bin/python3
# -*- coding: utf-8 -*-

import io
import os

import boto3
import numpy as np

REGION = os.environ.get("AWS_REGION", "eu-west-1")
BUCKET = os.environ.get("S3_BUCKET", "ucm-victor-del-pino-ucm-juegos")
CLAVE = os.environ.get("S3_KEY", "catalogo.npz")
MODELO = "all-MiniLM-L6-v2"

_cliente = None
_modelo = None
_catalogo = None


def cliente():
    global _cliente
    if _cliente is None:
        _cliente = boto3.client("s3", region_name=REGION)
    return _cliente


def modelo():
    global _modelo
    if _modelo is None:
        from sentence_transformers import SentenceTransformer

        _modelo = SentenceTransformer(MODELO)
    return _modelo


def catalogo():
    global _catalogo
    if _catalogo is None:
        cuerpo = cliente().get_object(Bucket=BUCKET, Key=CLAVE)["Body"].read()
        datos = np.load(io.BytesIO(cuerpo), allow_pickle=False)
        _catalogo = (
            datos["vectores"],
            datos["nombres"],
        )
    return _catalogo


def texto_catalogo(nombre, anio, minimo, maximo):
    return "%s. Año %s. Jugadores %s-%s." % (nombre, anio, minimo, maximo)


def embeber(texto):
    vector = modelo().encode(texto, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32)


def embeber_lote(textos):
    vectores = modelo().encode(textos, normalize_embeddings=True, batch_size=64)
    return np.asarray(vectores, dtype=np.float32)


def consultar(vector, limite):
    vectores, nombres = catalogo()
    if len(nombres) == 0:
        return []
    puntuaciones = vectores @ vector
    cantidad = min(limite, len(nombres))
    posiciones = np.argpartition(-puntuaciones, cantidad - 1)[:cantidad]
    orden = posiciones[np.argsort(-puntuaciones[posiciones])]
    return [(str(nombres[i]), float(puntuaciones[i])) for i in orden]


def recomendar(titulos, limite=5):
    consultados = []
    vistos = set()
    for titulo in titulos:
        limpio = titulo.strip()
        clave = limpio.casefold()
        if limpio == "" or clave in vistos:
            continue
        vistos.add(clave)
        consultados.append(limpio)

    if len(consultados) == 0:
        return [], [], list(titulos)

    acumulado = {}
    for titulo in consultados:
        for nombre, puntuacion in consultar(embeber(titulo), limite + len(consultados)):
            if nombre.casefold() in vistos:
                continue
            previo = acumulado.get(nombre)
            if previo is None or puntuacion > previo:
                acumulado[nombre] = puntuacion

    ordenados = sorted(acumulado, key=lambda nombre: acumulado[nombre], reverse=True)
    return ordenados[:limite], consultados, []
