# Juegotea

Recomendador de juegos de mesa. A partir de uno o varios títulos propone juegos que los mismos usuarios han puntuado con un 9 o más. El peso es cuántos usuarios comparten ese par. La tabla vive en S3.

El código parte del proyecto de la asignatura de sistemas de información. Este repositorio lo deja listo para instalar con [asdf](https://asdf-vm.com/) y para desplegar la página en la cuenta de AWS del curso de Terraform.

## Requisitos

[asdf](https://asdf-vm.com/) con los plugins `python` y `terraform`. Las versiones están fijadas en [`.tool-versions`](.tool-versions):

| Herramienta | Versión |
| --- | --- |
| Python | 3.12.15 |
| Terraform | 1.15.9 |

Hace falta una sesión de AWS en `eu-west-1` con permiso de lectura sobre el bucket de las recomendaciones.

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
| `consulta.py` | Baja `recomendaciones.json` de S3 y devuelve hasta veinte vecinos |
| `cargar_recomendaciones.py` | Cuenta los pares, se queda con los 20 vecinos de más peso y sube el JSON |
| `01_usuarios.py` | Descarga quien ha comentado los juegos origen y escribe `Files/usuarios.csv` |
| `02_datosJuegos.py` | Recorre esos usuarios, guarda una fila por juego y los pares con nota de al menos 9 |
| `terraform/` | Bucket, tarea y servicio. El documento está en [terraform/README.md](terraform/README.md) |

`01_usuarios.py` y `02_datosJuegos.py` se lanzan desde la raíz y necesitan la variable `BGG_TOKEN`. Sin ella se detienen y no vacían los CSV. `02_datosJuegos.py` pide una colección por usuario y escribe `Files/AristasJuegos.csv`. Después, `python cargar_recomendaciones.py` cuenta esos pares y sube `recomendaciones.json`. La página no lanza esos scripts.

Con un solo título, el resultado son los 20 vecinos de más peso. Con varios, se suman los pesos y se quitan los títulos pedidos. El peso es el número de usuarios.

En Git se quedan `Files/usuarios.csv` y `Files/NodosJuegos.csv`. `Files/AristasJuegos.csv` lo genera el paso 2 y no se versiona.

## Despliegue

La cuenta del curso es `eu-west-1`, con el usuario `ucm-victor_del_pino_ucm`. Esa cuenta no deja crear roles, grupos de seguridad ni otro repositorio de imágenes. El servicio se apoya en la VPC, el balanceador, los roles y el repositorio ECR que ya dejó el taller.

El detalle de cada fichero de Terraform, de lo que ya existe y de lo que crea este proyecto está en [terraform/README.md](terraform/README.md).
