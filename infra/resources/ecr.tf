resource "aws_ecr_repository" "this" {
  name                 = "${local.global_prefix_name}"
  image_tag_mutability = "IMMUTABLE"

  tags = local.tags
}

output "ecr_repository_url" {
  value = aws_ecr_repository.this.repository_url
}
