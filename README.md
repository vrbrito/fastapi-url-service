# FastAPI URL Service

Create a service deployed on AWS Lambda that provides access to private S3 bucket files through pre-signed urls tracking usage based on token authentication.

## Requirements

### Core

- [ ] Setup package manager
- [ ] Install FastAPI
- [ ] Create dummy endpoint
- [ ] Setup S3 integration
- [ ] Create endpoint to list files
- [ ] Create endpoint to retrieve pre-signed url for a specific file
- [ ] Setup linting and testing
- [ ] Setup persistence layer (DynamoDB?)
- [ ] Setup token auth to API
- [ ] Create usage measurements based on token auth

### Infra

- [ ] Setup base terraform for managing resources
- [ ] Setup S3 resource (make it fully private to avoid public access)
- [ ] Setup FastAPI deploy to AWS Lambda
- [ ] Setup CI/CD pipeline
