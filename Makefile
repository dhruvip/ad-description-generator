.PHONY: build
build:
	$(info --- docker compose down)
	docker build -t description-generator-poc .

.PHONY: up
up:
	$(info --- docker compose up)
	docker-compose -f docker-compose.yaml up

.PHONY: up-in-detach
up-in-detach:
	$(info --- docker compose up)
	docker-compose -f docker-compose.yaml up -d


.PHONY: clean
clean:
	$(info --- docker compose down)
	docker-compose -f docker-compose.yaml down