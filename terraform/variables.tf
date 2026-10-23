variable "aws_region" {
  description = "Región de la infra base."
  type        = string
  default     = "eu-west-1"
}

variable "identificador_alumno" {
  description = "Tu identificador, el mismo de tu usuario IAM sin el prefijo ucm-."
  type        = string
  default     = "victor_del_pino_ucm"
}

variable "imagen_tag" {
  description = "Etiqueta de la imagen en el ECR del taller. No usa latest."
  type        = string
  default     = "juegotea"
}

variable "numero_tareas" {
  description = "Tareas Fargate del servicio."
  type        = number
  default     = 1

  validation {
    condition     = var.numero_tareas == 1
    error_message = "1 tarea: el taller comparte subredes y presupuesto."
  }
}
