resource "aws_s3_bucket" "juegos" {
  bucket        = "${local.prefijo}-juegos"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "juegos" {
  bucket = aws_s3_bucket.juegos.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "juegos" {
  bucket = aws_s3_bucket.juegos.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "juegos" {
  bucket = aws_s3_bucket.juegos.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_object" "consulta" {
  provider     = aws.sin_etiquetas
  bucket       = aws_s3_bucket.juegos.id
  key          = "consulta.py"
  source       = "${path.module}/../consulta.py"
  source_hash  = filemd5("${path.module}/../consulta.py")
  content_type = "text/x-python"
}

resource "aws_s3_object" "web" {
  provider     = aws.sin_etiquetas
  bucket       = aws_s3_bucket.juegos.id
  key          = "web.py"
  source       = "${path.module}/../web.py"
  source_hash  = filemd5("${path.module}/../web.py")
  content_type = "text/x-python"
}

resource "aws_s3_object" "recomendaciones" {
  provider     = aws.sin_etiquetas
  bucket       = aws_s3_bucket.juegos.id
  key          = "recomendaciones.json"
  source       = "${path.module}/../recomendaciones.json"
  source_hash  = filemd5("${path.module}/../recomendaciones.json")
  content_type = "application/json"
}
