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


def pagina(consulta_texto, juegos, aviso):
    filas = ""
    for indice, juego in enumerate(juegos, start=1):
        anio = str(juego.get("anio", "")).strip()
        if anio in ("", "-1", "None"):
            detalle = ""
        else:
            detalle = " · " + html.escape(anio)
        peso = int(juego["peso"])
        if peso == 1:
            usuarios = "1 usuario"
        else:
            usuarios = "%d usuarios" % peso
        filas += '<li><span>%02d</span><div><strong>%s</strong><em>%s</em></div><small>%s</small></li>' % (
            indice, html.escape(juego["nombre"]), detalle, usuarios)
    if filas == "":
        lista = ""
    else:
        lista = '<section class="resultados"><h2>Coincidencias</h2><ol>%s</ol></section>' % filas
    aviso_html = ""
    if aviso:
        aviso_html = '<p class="aviso">%s</p>' % html.escape(aviso)
    accion = PREFIJO + "/"
    return PLANTILLA.replace("{{ACCION}}", html.escape(accion)).replace(
        "{{CONSULTA}}", html.escape(consulta_texto)
    ).replace("{{AVISO}}", aviso_html).replace("{{LISTA}}", lista)


PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Juegotea</title>
  <style>
    :root {
      --ink: #2b2118;
      --muted: #6d5c4b;
      --paper: #fbf6ee;
      --line: #e6d7c3;
      --clay: #9a4032;
      --clay-dark: #7c3126;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background-color: #e7dcc8;
      background-image: radial-gradient(#d4c4ab 1.1px, transparent 1.1px);
      background-size: 22px 22px;
    }
    main {
      width: min(40rem, calc(100% - 2rem));
      margin: 3.5rem auto;
      padding: 2.4rem 2rem 2rem;
      background: var(--paper);
      border: 1px solid #efe4d4;
      border-radius: 22px;
      box-shadow: 0 24px 50px rgba(70, 46, 24, 0.14);
    }
    .kicker {
      margin: 0;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-size: 0.72rem;
      color: var(--clay);
    }
    h1 {
      margin: 0.35rem 0 0.4rem;
      font-family: "Iowan Old Style", Palatino, Georgia, serif;
      font-size: 3.2rem;
      font-weight: 600;
      letter-spacing: -0.03em;
      line-height: 0.95;
    }
    .lead, .hint { color: var(--muted); }
    .lead { margin: 0 0 1.4rem; font-size: 1.05rem; }
    form { display: flex; gap: 0.6rem; }
    input {
      flex: 1;
      min-width: 0;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 999px;
      padding: 0.85rem 1.1rem;
      font: inherit;
      color: inherit;
    }
    input:focus { outline: 2px solid #e7b2a8; border-color: transparent; }
    button {
      border: 0;
      border-radius: 999px;
      padding: 0.85rem 1.2rem;
      background: var(--clay);
      color: #fffaf6;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover { background: var(--clay-dark); }
    .hint { margin: 0.7rem 0 0; font-size: 0.86rem; }
    .aviso {
      margin: 1.3rem 0 0;
      padding: 0.8rem 1rem;
      border-radius: 12px;
      background: #f8e7e2;
      color: var(--clay-dark);
    }
    .resultados { margin-top: 1.6rem; }
    h2 {
      margin: 0 0 0.8rem;
      font-family: "Iowan Old Style", Palatino, Georgia, serif;
      font-size: 1.35rem;
      font-weight: 600;
    }
    ol { list-style: none; margin: 0; padding: 0; }
    li {
      display: flex;
      align-items: center;
      gap: 0.9rem;
      padding: 0.85rem 0.2rem;
      border-top: 1px solid var(--line);
    }
    li span {
      width: 2rem;
      color: var(--clay);
      font-variant-numeric: tabular-nums;
      font-size: 0.85rem;
    }
    li div { flex: 1; min-width: 0; }
    li strong { font-weight: 600; }
    li em { font-style: normal; color: var(--muted); }
    li small { margin-left: auto; color: var(--muted); font-size: 0.85rem; white-space: nowrap; }
    @media (max-width: 640px) {
      main { margin: 1rem auto; padding: 1.6rem 1.1rem; }
      h1 { font-size: 2.5rem; }
      form { flex-direction: column; }
    }
  </style>
</head>
<body>
  <main>
    <p class="kicker">Juegos de mesa</p>
    <h1>Juegotea</h1>
    <p class="lead">Dime un título y te propongo los que más usuarios han puntuado con un 9 o más.</p>
    <form method="get" action="{{ACCION}}">
      <input id="q" name="q" value="{{CONSULTA}}" aria-label="Juegos" placeholder="&quot;Azul&quot; &quot;Wingspan&quot;">
      <button type="submit">Recomendar</button>
    </form>
    <p class="hint">Si el nombre tiene varias palabras, escríbelo entre comillas.</p>
    {{AVISO}}
    {{LISTA}}
  </main>
</body>
</html>
"""


@app.get(PREFIJO + "/health")
def health():
    return {"status": "ok"}


def inicio(q: str = ""):
    titulos = partir_consulta(q)
    if len(titulos) == 0:
        return pagina(q, [], "")
    try:
        juegos, _, _ = consulta.recomendar(titulos)
    except ClientError as error:
        return pagina(q, [], "No se ha podido consultar las recomendaciones: %s" % error)
    if len(juegos) == 0:
        return pagina(q, [], "No se ha encontrado información para los juegos introducidos")
    return pagina(q, juegos, "")


app.get(PREFIJO + "/", response_class=HTMLResponse)(inicio)
if PREFIJO:
    app.get(PREFIJO, response_class=HTMLResponse)(inicio)
