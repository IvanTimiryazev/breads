.PHONY: run
run: ## Run application
	docker compose up -d

.PHONY: stop
stop: ## Create a new revision file
	docker compose down
