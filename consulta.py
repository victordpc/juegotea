#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os

import boto3

REGION = os.environ.get("AWS_REGION", "eu-west-1")
BUCKET = os.environ.get("S3_BUCKET", "ucm-victor-del-pino-ucm-juegos")
CLAVE = os.environ.get("S3_KEY", "recomendaciones.json")
RUTA = os.environ.get("RECOMENDACIONES", "")
LIMITE = 20

_cliente = None
_tabla = None


def cliente():
    global _cliente
    if _cliente is None:
        _cliente = boto3.client("s3", region_name=REGION)
    return _cliente


def tabla():
    global _tabla
    if _tabla is None:
        if RUTA != "" and os.path.exists(RUTA):
            with open(RUTA, "r") as fichero:
                _tabla = json.load(fichero)
        else:
            cuerpo = cliente().get_object(Bucket=BUCKET, Key=CLAVE)["Body"].read()
            _tabla = json.loads(cuerpo)
    return _tabla


def recomendar(titulos, limite=LIMITE):
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

    datos = tabla()
    acumulado = {}
    for titulo in consultados:
        for vecino in datos.get(titulo.casefold(), []):
            if vecino["nombre"].casefold() in vistos:
                continue
            previo = acumulado.get(vecino["nombre"])
            if previo is None:
                acumulado[vecino["nombre"]] = {
                    "nombre": vecino["nombre"],
                    "anio": vecino["anio"],
                    "peso": int(vecino["peso"]),
                }
            else:
                previo["peso"] += int(vecino["peso"])

    ordenados = sorted(acumulado.values(), key=lambda juego: juego["peso"], reverse=True)
    return ordenados[:limite], consultados, []
