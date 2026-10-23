resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${local.prefijo}"
  retention_in_days = 7
}

resource "aws_ecs_cluster" "cluster" {
  name = "${local.prefijo}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

locals {
  arranque = <<-EOT
    pip install --no-cache-dir fastapi==0.161.1 uvicorn==0.54.0 boto3==1.43.118
    mkdir -p /opt/juegotea
    python -c 'import boto3, os
    s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])
    bucket = os.environ["S3_BUCKET"]
    destino = "/opt/juegotea"
    s3.download_file(bucket, "consulta.py", destino + "/consulta.py")
    s3.download_file(bucket, "web.py", destino + "/web.py")
    s3.download_file(bucket, os.environ["S3_KEY"], destino + "/recomendaciones.json")'
    cd /opt/juegotea
    export RECOMENDACIONES=/opt/juegotea/recomendaciones.json
    exec python -m uvicorn web:app --host 0.0.0.0 --port 8000
  EOT
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.prefijo}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.ecs_ejecucion.arn
  task_role_arn            = data.aws_iam_role.ecs_tarea.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = "public.ecr.aws/docker/library/python:3.12-slim-bookworm"
      essential = true
      command   = ["sh", "-c", local.arranque]
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }
      environment = [
        {
          name  = "API_ROOT_PATH"
          value = "/${local.prefijo}"
        },
        {
          name  = "S3_BUCKET"
          value = aws_s3_bucket.juegos.bucket
        },
        {
          name  = "S3_KEY"
          value = "recomendaciones.json"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "RECOMENDACIONES"
          value = "/opt/juegotea/recomendaciones.json"
        },
      ]
    }
  ])
}

resource "aws_lb_target_group" "api" {
  name        = "${local.prefijo}-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.base.id

  deregistration_delay = 30

  health_check {
    path                = "/${local.prefijo}/health"
    protocol            = "HTTP"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 15
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = data.aws_lb_listener.http.arn
  priority     = tonumber(data.aws_ssm_parameter.prioridad.insecure_value)

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = [
        "/${local.prefijo}",
        "/${local.prefijo}/*",
      ]
    }
  }
}

resource "aws_ecs_service" "api" {
  name            = "${local.prefijo}-api"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.numero_tareas
  launch_type     = "FARGATE"

  health_check_grace_period_seconds = 120

  network_configuration {
    subnets          = data.aws_subnets.privadas.ids
    security_groups  = [data.aws_security_group.tareas.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "fastapi"
    container_port   = 8000
  }

  triggers = {
    consulta        = aws_s3_object.consulta.etag
    web             = aws_s3_object.web.etag
    recomendaciones = aws_s3_object.recomendaciones.etag
  }

  depends_on = [
    aws_lb_listener_rule.api,
    aws_s3_object.consulta,
    aws_s3_object.web,
    aws_s3_object.recomendaciones,
  ]
}
