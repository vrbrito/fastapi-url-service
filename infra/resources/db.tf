resource "aws_dynamodb_table" "dynamodb-table" {
  name         = local.global_prefix_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "entityIdentifier"
  range_key    = "dataType"

  attribute {
    name = "entityIdentifier"
    type = "S"
  }

  attribute {
    name = "dataType"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  attribute {
    name = "createdOn"
    type = "S"
  }

  global_secondary_index {
    name            = "emailIndex"
    hash_key        = "email"
    range_key       = "createdOn"
    projection_type = "ALL"
  }

  tags = local.tags
}
