data "aws_vpc" "base" {
  tags = {
    Name = "ucm-proyecto-final-vpc"
  }
}

data "aws_subnets" "privadas" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.base.id]
  }

  tags = {
    Tier = "privada"
  }
}

data "aws_security_group" "tareas" {
  name   = "ucm-proyecto-final-tareas"
  vpc_id = data.aws_vpc.base.id
}

data "aws_lb" "base" {
  name = "ucm-proyecto-final-alb"
}

data "aws_lb_listener" "http" {
  load_balancer_arn = data.aws_lb.base.arn
  port              = 80
}

data "aws_ssm_parameter" "prioridad" {
  name = "/ucm/proyecto-final/${var.identificador_alumno}/prioridad"
}

data "aws_ecr_repository" "fastapi" {
  name = "ucm-proyecto-final-fastapi"
}

data "aws_iam_role" "ecs_ejecucion" {
  name = "ucm-ecs-ejecucion"
}

data "aws_iam_role" "ecs_tarea" {
  name = "ucm-ecs-tarea"
}

locals {
  alumno  = replace(var.identificador_alumno, "_", "-")
  prefijo = "ucm-${local.alumno}"
}
