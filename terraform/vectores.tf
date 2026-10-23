resource "aws_s3_bucket" "juegos" {
  bucket = "${local.prefijo}-juegos"
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
