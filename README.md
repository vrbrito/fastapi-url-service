# FastAPI URL Service

Create a service deployed on AWS Lambda that provides access to private S3 bucket files through pre-signed urls tracking usage based on token authentication.

## Stack

- **Application core**: Python + FastAPI
- **Package manager**: Poetry
- **Testing**: Pytest + Moto
- **Infrastructure management**: Terraform
- **Cloud services**: AWS Lambda + DynamoDB + S3

## Requirements

### Core

- [x] Setup package manager
- [x] Install FastAPI
- [x] Create dummy endpoint
- [x] Setup S3 integration
- [x] Create endpoint to list files
- [x] Create endpoint to retrieve pre-signed url for a specific file
- [x] Setup linting
- [x] Setup testing
- [x] Improve testing to use factory boy
- [x] Improve testing by using moto to mock AWS services
- [x] Setup persistence layer (DynamoDB?)
- [x] Create endpoint to add new user
- [ ] Setup token auth to API
- [ ] Create usage measurements based on token auth

### Infra

- [x] Setup base terraform for managing resources
- [x] Setup S3 resource (make it fully private to avoid public access)
- [x] Setup DynamoDB resource
- [x] Setup FastAPI deploy to AWS Lambda
- [ ] Adjust role to include S3 and DynamoDB permissions
- [ ] Setup CI/CD pipeline
- [ ] Integrate project with localstack for easy local testing

### Architecture

- [ ] Improve code architecture by evaluating including service/repo layers

### Bugs

- [ ] Redirect loop happening on the deployed version of the app

## Database

For this project, a single-table approach was chosen to be used on DynamoDB, for this, listing the use-cases is very important.

### Use cases

- Check if user token exists (read)
- Register new user (write)
  - Email must be unique across all users
- Register usage for each new request (write)
