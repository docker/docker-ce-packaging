SHELL:=/bin/bash
ENGINE_DIR:=$(CURDIR)/../../engine
CLI_DIR:=$(CURDIR)/../../cli
VERSION?=0.0.0-dev
GO_BASE_IMAGE=golang
GO_VERSION:=1.10.4
GO_IMAGE=$(GO_BASE_IMAGE):$(GO_VERSION)
STATIC_VERSION=$(shell ../static/gen-static-ver $(ENGINE_DIR) $(VERSION))
DOCKER_HUB_ORG?=docker
ARCH=$(shell uname -m)
ENGINE_IMAGE?=engine-community
DEFAULT_PRODUCT_LICENSE?=Community Engine
TAG=$(STATIC_VERSION).$(ARCH)
IMAGE_WITH_TAG=$(DOCKER_HUB_ORG)/$(ENGINE_IMAGE):$(TAG)
IMAGE_BUILD=docker build -t $(IMAGE_WITH_TAG) \
	--build-arg GO_IMAGE="$(GO_IMAGE)" \
	--build-arg VERSION="$(STATIC_VERSION)" \
	--build-arg GITCOMMIT="$$(cd $(ENGINE_DIR) && git rev-parse --short=7 HEAD)" \
	--build-arg BUILDTIME="$(BUILDTIME)" \
	--build-arg PLATFORM="$(PLATFORM)" \
	--build-arg PRODUCT="$(PRODUCT)" \
	--build-arg DEFAULT_PRODUCT_LICENSE="$(DEFAULT_PRODUCT_LICENSE)" \
	--file $< $(ENGINE_DIR)

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	-$(RM) $(ENGINE_DIR)/Dockerfile.engine
	-$(RM) $(ENGINE_DIR)/Dockerfile.engine-dm
	-docker rmi $(IMAGE_WITH_TAG)
	-rm -f image-linux-*

.PHONY: image
image: image-linux

$(ENGINE_DIR)/Dockerfile.%: Dockerfile.%
	cp $< $@

# builds across multiple archs because the base images
# utilize manifests
image-linux: $(ENGINE_DIR)/Dockerfile.engine
	./image_exists $(IMAGE_WITH_TAG) || $(IMAGE_BUILD)
	echo $(IMAGE_WITH_TAG) > $@

image-linux-dm: $(ENGINE_DIR)/Dockerfile.engine-dm
	$(warning WARN: This image will be named: $(IMAGE_WITH_TAG)-dm)
	./image_exists $(IMAGE_WITH_TAG)-dm || $(IMAGE_BUILD)
	echo $(IMAGE_WITH_TAG) > $@

engine-$(ARCH).tar: image-linux
	docker save -o $@ $$(cat $<)

.PHONY: release
release:
	docker push $(IMAGE_WITH_TAG)
