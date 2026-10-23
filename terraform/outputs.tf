output "url_api" {
  description = "URL de la página, con el prefijo de este alumno."
  value       = "http://${data.aws_lb.base.dns_name}/${local.prefijo}/"
}

output "bucket_vectores" {
  description = "Bucket con recomendaciones.json."
  value       = aws_s3_bucket.juegos.bucket
}
