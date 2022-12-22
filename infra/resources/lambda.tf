resource "aws_iam_role" "api_role" {
  name = "${local.global_prefix_name}-api-role"
  
  inline_policy {
    name = "resource_access"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = [
            "cloudwatch:*",
            "logs:*",
          ]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }
  
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
  })
}

resource "aws_lambda_function" "api" {
  function_name = "${local.global_prefix_name}-api"
  role          = aws_iam_role.api_role.arn

  package_type = "Image"
  image_uri    = var.lambda_image_uri

  memory_size = 512
  timeout     = 28
}

resource "aws_lambda_function_url" "api_url" {
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "NONE"
}

output "lambda_function_url" {
  value = aws_lambda_function_url.api_url.function_url
}
