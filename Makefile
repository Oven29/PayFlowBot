# Default target
.DEFAULT_GOAL := help

.PHONY: build run stop remove check logs migrate docker-build docker-run docker-stop docker-remove docker-clean run-bot stop-bot clean-bot help

### Dev commands
dev:  ## Run bot (for dev)
	python main.py

migrate:  ## Run all migrations
	mkdir -p data
	alembic upgrade head

# create-migration msg="comment (optional)"
create-migration:  ## Create migrations, usage with optional msg=""
	alembic revision --autogenerate -m "$(msg)"

# Workaround for passing arguments to `make`
%:
	@:

### Docker Compose commands
build:  ## Docker compose build
	docker-compose build

run:  ## Docker compose run and build if not built
	docker-compose up -d

stop:  ## Docker compose stop
	docker-compose down

remove:  ## Docker compose remove
	docker-compose down -v
	docker rmi payflowbot-bot

status:  ## Check statuses docker containers
	docker-compose ps -a

logs:  ## Docker compose logs
	@docker-compose logs -f

### Docker direct commands
docker-build:  ## Build image from Dockerfile (build bot)
	docker build -t PayFlowBot .

docker-run:  ## Run bot container
	docker run -d --name PayFlowBot-container

docker-stop:  ## Stop bot container
	docker stop PayFlowBot-container

docker-remove:  ## Remove container
	docker rm PayFlowBot-container

docker-clean:  ## Remove image
	docker rmi PayFlowBot

### Combined workflow
run-bot: docker-build docker-run  ## Build and run container without docker-compose
stop-bot: docker-stop docker-remove  ## Stop and remove container
clean-bot: stop-bot docker-clean  ## Stop and remove container with image

### Help command
help: ## Displaying a list of available commands with descriptions
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
