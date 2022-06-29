include ../common.mk

CLI_DIR=$(realpath $(CURDIR)/../src/github.com/docker/cli)
ENGINE_DIR=$(realpath $(CURDIR)/../src/github.com/docker/docker)
BUILDX_DIR=$(realpath $(CURDIR)/../src/github.com/docker/buildx)
COMPOSE_DIR=$(realpath $(CURDIR)/../src/github.com/docker/compose)
SCAN_DIR=$(realpath $(CURDIR)/../src/github.com/docker/scan-cli-plugin)

STATIC_VERSION=$(shell ./gen-static-ver $(CLI_DIR) $(VERSION))
HASH_CMD=docker run -v $(CURDIR):/sum -w /sum debian:jessie bash hash_files
DIR_TO_HASH:=build/linux

export CLI_DIR
export ENGINE_DIR
export BUILDX_DIR
export COMPOSE_DIR
export SCAN_DIR

export STATIC_VERSION
export CONTAINERD_VERSION
export RUNC_VERSION

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	$(call title,Removing build artifacts)
	@[ ! -d build ] || $(CHOWN) -R $(shell id -u):$(shell id -g) build
	@$(RM) -r build

.PHONY: build
build: ## build static package
	$(call title,Building static package for $(TARGETPLATFORM))
	./build-static "$(CURDIR)" "$(TARGETPLATFORM)"

.PHONY: hash_files
hash_files: ## hash files
	$(call title,Hashing directory $(DIR_TO_HASH))
	$(HASH_CMD) "$(DIR_TO_HASH)"
