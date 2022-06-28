include ../common.mk

CLI_DIR=$(realpath $(CURDIR)/../src/github.com/docker/cli)
ENGINE_DIR=$(realpath $(CURDIR)/../src/github.com/docker/docker)
BUILDX_DIR=$(realpath $(CURDIR)/../src/github.com/docker/buildx)

STATIC_VERSION=$(shell ./gen-static-ver $(CLI_DIR) $(VERSION))
HASH_CMD=docker run -v $(CURDIR):/sum -w /sum debian:jessie bash hash_files
DIR_TO_HASH:=build/linux

export CLI_DIR
export ENGINE_DIR
export BUILDX_DIR

export STATIC_VERSION
export CONTAINERD_VERSION
export RUNC_VERSION

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BOLD)$(CYAN)%-25s$(RESET)%s\n", $$1, $$2}'

.PHONY: clean
clean: ## remove build artifacts
	@[ ! -d build ] || $(CHOWN) -R $(shell id -u):$(shell id -g) build
	@$(RM) -r build

.PHONY: build
build: ## build static package
	./build-static "$(CURDIR)" "$(TARGETPLATFORM)"

.PHONY: hash_files
hash_files: ## hash files
	@echo "Hashing directory $(DIR_TO_HASH)"
	$(HASH_CMD) "$(DIR_TO_HASH)"
