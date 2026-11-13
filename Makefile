.PHONY: help setup generate-secret build up down logs clean restart test

help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file"; \
	else \
		echo ".env file already exists"; \
	fi
	@$(MAKE) generate-secret

generate-secret:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@SECRET=$$(openssl rand -base64 64 | tr -d '\n'); \
	if grep -q "^JWT_SECRET=" .env; then \
		sed -i.bak "s|^JWT_SECRET=.*|JWT_SECRET=$$SECRET|" .env && rm -f .env.bak; \
	else \
		echo "JWT_SECRET=$$SECRET" >> .env; \
	fi
	@echo "JWT_SECRET generated and saved to .env"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Application running at http://localhost:3000"
	@echo "API docs at http://localhost:3000/api"

down:
	docker-compose down

logs:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f postgres

restart:
	docker-compose restart app

clean:
	docker-compose down -v
	docker system prune -f

shell:
	docker-compose exec app sh

db-shell:
	docker-compose exec postgres psql -U postgres -d drone_delivery

migrate:
	docker-compose exec app npx prisma migrate deploy

migrate-dev:
	docker-compose exec app npx prisma migrate dev

seed:
	docker-compose exec app npx prisma db seed

test:
	docker-compose exec app npm run test

test-e2e:
	docker-compose exec app npm run test:e2e

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

health:
	@curl -s http://localhost:3000/health | jq '.'

ps:
	docker-compose ps
