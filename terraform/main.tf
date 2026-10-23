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

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.prefijo}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "2048"
  execution_role_arn       = data.aws_iam_role.ecs_ejecucion.arn
  task_role_arn            = data.aws_iam_role.ecs_tarea.arn

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = "${data.aws_ecr_repository.fastapi.repository_url}:${var.imagen_tag}"
      essential = true
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
          value = "catalogo.npz"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "HF_HUB_OFFLINE"
          value = "1"
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

  health_check_grace_period_seconds = 180

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

  depends_on = [aws_lb_listener_rule.api]
}
