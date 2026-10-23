# Terraform de Juegotea

Publica la página del recomendador en el balanceador del taller y guarda `recomendaciones.json` en un bucket de S3. La región es `eu-west-1`. No se crea otra red, otro balanceador, otros roles ni otro repositorio de imágenes.

## Qué hay en esta carpeta

| Fichero | Qué declara |
| --- | --- |
| `versions.tf` | Terraform `>= 1.10.0` y el provider AWS `~> 6.0` |
| `provider.tf` | Región y etiquetas comunes |
| `variables.tf` | Identificador del alumno y número de tareas |
| `data.tf` | Lo que ya existe en la cuenta, y el prefijo `ucm-` |
| `vectores.tf` | Bucket del catálogo, cifrado y bloqueo de acceso público |
| `main.tf` | Log group, clúster, tarea, target group, regla del listener y servicio |
| `outputs.tf` | URL de la página y nombre del bucket |
| `terraform.tfvars.example` | Valores de este alumno |

El estado (`terraform.tfstate`) no va en Git. El lock del provider sí.

## Nombres

`identificador_alumno` es el usuario IAM sin el prefijo `ucm-`. El valor por defecto es `victor_del_pino_ucm`. Donde el nombre no admite guion bajo, el guion bajo pasa a guion:

| Pieza | Nombre |
| --- | --- |
| Prefijo y ruta del balanceador | `ucm-victor-del-pino-ucm` |
| Bucket | `ucm-victor-del-pino-ucm-juegos` |
| Objeto de las recomendaciones | `recomendaciones.json` |
| Clúster | `ucm-victor-del-pino-ucm-cluster` |
| Servicio y familia de la tarea | `ucm-victor-del-pino-ucm-api` |
| Target group | `ucm-victor-del-pino-ucm-tg` |
| Log group | `/ecs/ucm-victor-del-pino-ucm` |
| Imagen | `public.ecr.aws/docker/library/python:3.12-slim-bookworm` |

La prioridad de la regla del listener no se escribe aquí. Se lee de SSM, en `/ucm/proyecto-final/victor_del_pino_ucm/prioridad`.

## Lo que ya existe

`data.tf` solo lee. No crea la VPC, el balanceador, los roles ni el repositorio.

| Data source | Recurso del taller |
| --- | --- |
| `aws_vpc.base` | `ucm-proyecto-final-vpc` |
| `aws_subnets.privadas` | Subredes de esa VPC con la etiqueta `Tier=privada` |
| `aws_security_group.tareas` | `ucm-proyecto-final-tareas` |
| `aws_lb.base` | `ucm-proyecto-final-alb` |
| `aws_lb_listener.http` | Listener del puerto 80 |
| `aws_ssm_parameter.prioridad` | Prioridad asignada a este alumno |
| `aws_ecr_repository.fastapi` | `ucm-proyecto-final-fastapi` |
| `aws_iam_role.ecs_ejecucion` | `ucm-ecs-ejecucion` |
| `aws_iam_role.ecs_tarea` | `ucm-ecs-tarea` |

`local.prefijo` sale de `identificador_alumno`. El resto de ficheros usa ese prefijo.

## Bucket del catálogo

`vectores.tf` crea `ucm-victor-del-pino-ucm-juegos`.

El cifrado es AES256, el de S3 en reposo. El acceso público está bloqueado y el propietario del bucket es el dueño de los objetos. El tráfico de la aplicación va por HTTPS.

La cuenta de este alumno puede crear buckets cuyo nombre empieza por `ucm-`. No puede crear un bucket de S3 Vectors ni una tabla de DynamoDB, y el rol `ucm-ecs-tarea` tampoco puede consultar esos servicios. Sí puede leer objetos de buckets `ucm-*`. La consulta baja `recomendaciones.json` y resuelve el peso en el proceso.

`cargar_recomendaciones.py`, en la raíz del repositorio, es quien sube ese objeto. Terraform crea el bucket y no sube el fichero.

## Servicio

`main.tf` deja una tarea Fargate de arquitectura ARM64. Son 0,25 vCPU y 512 MB. El contenedor se llama `fastapi` y escucha en el puerto 8000. No tiene IP pública. Sale a Internet por el NAT del taller, en las subredes privadas, con el grupo `ucm-proyecto-final-tareas`.

El rol de ejecución escribe en el log group, con retención de 7 días. El rol de la tarea lee el bucket. La imagen pública no sale del ECR del taller: este usuario no puede subir capas a ese repositorio.

La regla del listener reenvía `/ucm-victor-del-pino-ucm` y `/ucm-victor-del-pino-ucm/*`. El balanceador no quita ese prefijo, así que la página y `/health` viven debajo. El target group comprueba `/${prefijo}/health` y espera un 200. El servicio espera 120 segundos antes de dar la tarea por enferma. En ese margen instala FastAPI y baja `consulta.py`, `web.py` y `recomendaciones.json`.

Variables de entorno de la tarea:

| Variable | Valor |
| --- | --- |
| `API_ROOT_PATH` | `/ucm-victor-del-pino-ucm` |
| `S3_BUCKET` | El bucket de `vectores.tf` |
| `S3_KEY` | `recomendaciones.json` |
| `AWS_REGION` | `eu-west-1` |
| `RECOMENDACIONES` | `/opt/juegotea/recomendaciones.json` |

`numero_tareas` tiene que ser 1. El taller comparte subredes y presupuesto.

## Imagen

La tarea arranca `public.ecr.aws/docker/library/python:3.12-slim-bookworm`. Al entrar instala FastAPI, Uvicorn y `boto3`, y baja `consulta.py`, `web.py` y `recomendaciones.json` del bucket. Después lanza `uvicorn` en el puerto 8000.

El repositorio ECR del taller y su etiqueta `latest` no se tocan: la cuenta no deja subir una etiqueta propia.

El target group, el clúster y el servicio usan los mismos nombres que la API de menús del ejercicio de clase. Esa API tiene que estar destruida antes del apply: dos reglas no comparten prioridad y una segunda tarea se come el presupuesto del taller.

## Aplicar

Desde esta carpeta, con las credenciales del alumno:

```bash
terraform init
terraform plan
terraform apply
```

La salida `url_api` es la página. `bucket_vectores` es el bucket del catálogo.

Para repetir el despliegue de otra persona se cambia `identificador_alumno` en un `terraform.tfvars` copiado del ejemplo. El `.gitignore` excluye `*.tfvars` y deja el ejemplo.
