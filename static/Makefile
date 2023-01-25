include ../common.mk

CLI_DIR=$(realpath $(CURDIR)/../src/github.com/docker/cli)
ENGINE_DIR=$(realpath $(CURDIR)/../src/github.com/docker/docker)
BUILDX_DIR=$(realpath $(CURDIR)/../src/github.com/docker/buildx)

ENGINE_GITCOMMIT?=$(shell cd $(realpath $(CURDIR)/../src/github.com/docker/docker) && git rev-parse --short HEAD)
GEN_STATIC_VER=$(shell ./gen-static-ver $(CLI_DIR) $(VERSION))
HASH_CMD=docker run -v $(CURDIR):/sum -w /sum debian:jessie bash hash_files
DIR_TO_HASH:=build/linux

# Select the default version of containerd and runc based on the docker engine
# source we need this variable here for naming the produced .tgz file.
CONTAINERD_VERSION?=$(shell grep "ARG CONTAINERD_VERSION" "$(ENGINE_DIR)/Dockerfile" | awk -F'=' '{print $$2}')
RUNC_VERSION?=$(shell grep "ARG RUNC_VERSION" "$(ENGINE_DIR)/Dockerfile" | awk -F'=' '{print $$2}')

export CLI_DIR
export ENGINE_DIR
export BUILDX_DIR
export GEN_STATIC_VER
export CONTAINERD_VERSION
export RUNC_VERSION

export REF
export DOCKER_CLI_REF
export DOCKER_ENGINE_REF
export DOCKER_SCAN_REF
export DOCKER_COMPOSE_REF
export DOCKER_BUILDX_REF

export GO_VERSION

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	@[ ! -d build ] || $(CHOWN) -R $(shell id -u):$(shell id -g) build
	@$(RM) -r build

.PHONY: create_builder
create_builder: # create docker-container builder
	docker buildx inspect | tr -d ' ' | grep -q 'Driver:docker-container' || docker buildx create --use --bootstrap

.PHONY: build
build: create_builder ## build static package
	CURDIR=$(CURDIR) TARGETPLATFORM=$(TARGETPLATFORM) ./build-static

.PHONY: hash_files
hash_files: ## hash files
	$(HASH_CMD) "$(DIR_TO_HASH)"
