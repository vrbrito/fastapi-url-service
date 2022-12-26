build-dev:
	docker build -t url-service-dev -f Dockerfile.dev .

build:
	docker build -t url-service -f Dockerfile .

run-dev:
	docker run --name url-service-dev --detach url-service-dev

run:
	docker run --name url-service --detach url-service

check:
	docker exec -t url-service-dev black --check "/var/task/app"
	docker exec -t url-service-dev isort --check "/var/task/app"
	docker exec -t url-service-dev flake8 "/var/task/app"
	docker exec -t url-service-dev safety check --full-report
	docker exec -t url-service-dev bandit -ll -r "/var/task/app"

test:
	docker exec -t url-service-dev pytest "/var/task/tests"
