
# Settings

APP           ?= vocabulary-test
IMAGE         ?= $(APP):latest
CONTAINER     ?= $(APP)-cont

DOCKERFILE    ?= Dockerfile
BUILD_CTX     ?= .

PORTS         ?=

ENV_OPT       ?=

PLATFORM      ?=

BUILD_ARGS    ?=

WORKDIR_HOST  ?= $(shell pwd)/workdir
WORKDIR_CONT  ?= /workdir

USER_FLAG     ?=

EXTRA_VOLUMES ?=

CMD           ?= bash


.PHONY: help build rebuild-nocache run dev

help:
	@echo "Targets:"
	@echo "  make build"
	@echo "    docker build -t $(IMAGE) "
	@echo "  make rebuild-nocache"
	@echo "    docker build -t --no-cache $(IMAGE)"
	@echo "  make help"
	@echo "    show this help  "	

build:
	docker build $(PLATFORM) -f $(DOCKERFILE) $(BUILD_ARGS) -t $(IMAGE) $(BUILD_CTX)

rebuild-nocache:
	docker build $(PLATFORM) -f $(DOCKERFILE) $(BUILD_ARGS) --no-cache -t $(IMAGE) $(BUILD_CTX)

run:
	docker run -d --name $(CONTAINER) $(IMAGE)

dev:
	docker run --rm -it \
	--name $(CONTAINER) \
	-v $(WORKDIR_HOST):$(WORKDIR_CONT) \
        -w $(WORKDIR_CONT) \
	$(IMAGE) $(CMD)
