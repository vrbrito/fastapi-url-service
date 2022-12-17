import os

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "url-service-dev-files")
AWS_DYNAMODB_TABLE_NAME = os.getenv("AWS_DYNAMODB_TABLE_NAME", "url-service-dev")
