#!/usr/bin/python3
# -*- coding: utf-8 -*-

import html
import os
import shlex

from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import consulta

PREFIJO = os.environ.get("API_ROOT_PATH", "").rstrip("/")
app = FastAPI()


def partir_consulta(texto):
    texto = texto.strip()
    if texto == "":
        return []
    try:
        return shlex.split(texto)
    except ValueError:
        return texto.split()


def pagina(consulta_texto, nombres, aviso):
    filas = ""
    for nombre in nombres:
        filas += "<li>%s</li>" % html.escape(nombre)
    if filas == "":
        lista = ""
    else:
        lista = "<ol>%s</ol>" % filas
    aviso_html = ""
    if aviso:
        aviso_html = "<p>%s</p>" % html.escape(aviso)
    accion = PREFIJO + "/"
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Juegotea</title>
  <style>
    body { font-family: Georgia, serif; margin: 2rem auto; max-width: 40rem; color: #1c1917; }
    form { display: flex; gap: 0.5rem; }
    input { flex: 1; font: inherit; padding: 0.4rem; }
    button { font: inherit; padding: 0.4rem 0.8rem; }
  </style>
</head>
<body>
  <h1>Juegotea</h1>
  <p>Escribe uno o varios juegos. Un nombre de varias palabras va entre comillas.</p>
  <form method="get" action="%s">
    <input name="q" value="%s" aria-label="Juegos">
    <button type="submit">Recomendar</button>
  </form>
  %s
  %s
</body>
</html>""" % (html.escape(accion), html.escape(consulta_texto), aviso_html, lista)


@app.get(PREFIJO + "/health")
def health():
    return {"status": "ok"}


def inicio(q: str = ""):
    titulos = partir_consulta(q)
    if len(titulos) == 0:
        return pagina(q, [], "")
    try:
        nombres, _, _ = consulta.recomendar(titulos)
    except ClientError as error:
        return pagina(q, [], "No se ha podido consultar el índice: %s" % error)
    if len(nombres) == 0:
        return pagina(q, [], "No se ha encontrado información para los juegos introducidos")
    return pagina(q, nombres, "")


app.get(PREFIJO + "/", response_class=HTMLResponse)(inicio)
if PREFIJO:
    app.get(PREFIJO, response_class=HTMLResponse)(inicio)
