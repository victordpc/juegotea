# Juegotea

Recomendador de juegos de mesa. Construye un grafo a partir de la API de [BoardGameGeek](https://boardgamegeek.com/wiki/page/BGG_XML_API2) y, a partir de uno o varios títulos, propone juegos afines.

El código parte del proyecto de la asignatura de sistemas de información. Este repositorio lo deja listo para instalar con [asdf](https://asdf-vm.com/) y, en el paso siguiente, desplegarlo en la cuenta de AWS del curso de Terraform.

## Requisitos

[asdf](https://asdf-vm.com/) con los plugins `python` y `terraform`. Las versiones están fijadas en [`.tool-versions`](.tool-versions):

| Herramienta | Versión |
| --- | --- |
| Python | 3.12.15 |
| Terraform | 1.15.9 |

Terraform 1.15.9 es la versión del curso. Python 3.12 es el runtime que usa la cuenta en Lambda.

## Puesta en marcha

Desde la raíz del repositorio:

```bash
asdf install
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python Juegotea.py "10 Days in Africa"
```

`Juegotea.py -h` muestra la ayuda. Los nombres de varias palabras van entre comillas. Sin argumentos, el programa pide la ayuda.

La salida esperada para ese ejemplo incluye Agricola, Acquire, Ubongo, Castles of Mad King Ludwig y Azul.

## Cómo está organizado

El recomendador que se ejecuta a mano es `Juegotea.py`. Lee dos CSV ya calculados:

| Fichero | Para qué |
| --- | --- |
| `Files/NodosJuegos.csv` | Identificador y nombre de cada juego |
| `Files/Recomendaciones.csv` | Vecinos y peso de cada juego |

El resto de scripts regenera esos datos. Hay que lanzarlos en este orden, desde la raíz, con la red disponible para los dos primeros:

1. `01_usuarios.py` descarga usuarios que han comentado juegos semilla en BoardGameGeek y escribe `Files/usuarios.csv`.
2. `02_datosJuegos.py` recorre esos usuarios y saca los juegos de su biblioteca.
3. `03_constructorNodos.py` construye los nodos del grafo.
4. `04_constructorAristas.py` construye las aristas.
5. `05_recomendador.py` calcula, con NetworkX, el CSV que luego consulta `Juegotea.py`.

`Files/AristasGrafo.csv`, `Files/AristasJuegos.csv` y `Files/NodosGrafo.csv` son intermedios de ese proceso. No van en Git: se vuelven a generar y pesan decenas de megabytes. `Files/NodosJuegos.csv` sí va en el repositorio porque sin él el recomendador no arranca.

## Despliegue

La cuenta del curso es `eu-west-1`, con el usuario `ucm-victor_del_pino_ucm`. Esa cuenta no deja crear roles, grupos de seguridad ni otro repositorio de imágenes. El servicio tiene que apoyarse en la VPC, el balanceador, los roles y el repositorio ECR que ya dejó el taller.

Hoy la ruta `/ucm-victor-del-pino-ucm` del balanceador la ocupa la API de menús del ejercicio de clase. Dos reglas no pueden compartir la prioridad asignada al alumno, así que Juegotea entra en ese hueco cuando se retire ese servicio.
