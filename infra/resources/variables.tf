variable "aws_region" {
  default     = "us-east-1"
  description = "This is the AWS region. It must be provided, but it can also be sourced from the AWS_DEFAULT_REGION environment variables, or via a shared credentials file if profile is specified."
}

variable "lambda_image_uri" {
  description = "ECR URI for the tagged image to be used on AWS Lambda deployment."
}
