# Juegotea

Recomendador de juegos de mesa. A partir de uno o varios títulos propone juegos parecidos. El catálogo vive en S3 y la consulta compara embeddings en la propia aplicación.

El código parte del proyecto de la asignatura de sistemas de información. Este repositorio lo deja listo para instalar con [asdf](https://asdf-vm.com/) y para desplegar la página en la cuenta de AWS del curso de Terraform.

## Requisitos

[asdf](https://asdf-vm.com/) con los plugins `python` y `terraform`. Las versiones están fijadas en [`.tool-versions`](.tool-versions):

| Herramienta | Versión |
| --- | --- |
| Python | 3.12.15 |
| Terraform | 1.15.9 |

Hace falta una sesión de AWS en `eu-west-1` con permiso de lectura sobre el bucket del catálogo.

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

La página usa la misma consulta. En local:

```bash
API_ROOT_PATH=/ucm-victor-del-pino-ucm python -m uvicorn web:app --host 127.0.0.1 --port 8000
```

La ruta es `http://127.0.0.1:8000/ucm-victor-del-pino-ucm/` y la comprobación `http://127.0.0.1:8000/ucm-victor-del-pino-ucm/health`.

## Cómo está organizado

| Pieza | Para qué |
| --- | --- |
| `Juegotea.py` | Consola. Llama a `consulta.recomendar` |
| `web.py` | Página FastAPI en el puerto 8000 |
| `consulta.py` | Baja `catalogo.npz` de S3 y devuelve hasta cinco nombres |
| `cargar_indice.py` | Lee `Files/NodosJuegos.csv`, calcula los embeddings y sube el fichero |
| `01_usuarios.py` | Descarga quien ha comentado Azul (`230802`) y escribe `Files/usuarios.csv` |
| `02_datosJuegos.py` | Recorre esos usuarios y deja una fila por juego en `Files/NodosJuegos.csv` |
| `terraform/` | Bucket, tarea y servicio. El documento está en [terraform/README.md](terraform/README.md) |
| `grafo/` | Construcción antigua del grafo. La consulta no la usa |

`01_usuarios.py` y `02_datosJuegos.py` se lanzan desde la raíz y necesitan la variable `BGG_TOKEN`. Sin ella se detienen y no vacían los CSV. Después, `python cargar_indice.py` vuelve a subir el catálogo. La página no lanza esos scripts.

El texto que se embebe junta el nombre, el año y los jugadores. El modelo es `all-MiniLM-L6-v2`, en local, con 384 dimensiones.

En Git se quedan `Files/usuarios.csv` y `Files/NodosJuegos.csv`, que son la entrada de esa carga. `Files/Recomendaciones.csv` y los CSV de aristas ya no se usan: los genera `grafo/` si se vuelve a lanzar, y no se versionan.

## Despliegue

La cuenta del curso es `eu-west-1`, con el usuario `ucm-victor_del_pino_ucm`. Esa cuenta no deja crear roles, grupos de seguridad ni otro repositorio de imágenes. El servicio se apoya en la VPC, el balanceador, los roles y el repositorio ECR que ya dejó el taller.

El detalle de cada fichero de Terraform, de lo que ya existe y de lo que crea este proyecto está en [terraform/README.md](terraform/README.md).
