include ../common.mk

CLI_DIR     = $(realpath $(CURDIR)/../src/github.com/docker/cli)
ENGINE_DIR  = $(realpath $(CURDIR)/../src/github.com/docker/docker)
BUILDX_DIR  = $(realpath $(CURDIR)/../src/github.com/docker/buildx)

GEN_STATIC_VER=$(shell ./gen-static-ver $(CLI_DIR) $(VERSION))
HASH_CMD=docker run -v $(CURDIR):/sum -w /sum debian:jessie bash hash_files
DIR_TO_HASH:=build/linux
DOCKER_CLI_GOLANG_IMG=golang:$(GO_VERSION)

DOCKER_BUILD_OPTS=

ifneq ($(strip $(CONTAINERD_VERSION)),)
# Set custom build-args to override the containerd version to build for static
# packages. The Dockerfile for 20.10 and earlier used CONTAINERD_COMMIT, later
# versions use CONTAINERD_VERSION. We can remove CONTAINERD_VERSION once 20.10.x
# reaches EOL.
DOCKER_BUILD_OPTS +=--build-arg=CONTAINERD_VERSION=$(CONTAINERD_VERSION)
DOCKER_BUILD_OPTS +=--build-arg=CONTAINERD_COMMIT=$(CONTAINERD_VERSION)
endif

ifneq ($(strip $(RUNC_VERSION)),)
# Set custom build-args to override the runc version to build for static packages.
DOCKER_BUILD_OPTS +=--build-arg=RUNC_VERSION=$(RUNC_VERSION)
endif

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	[ ! -d build ] || $(CHOWN) -R $(shell id -u):$(shell id -g) build
	$(RM) -r build
	-docker builder prune -f --filter until=24h

.PHONY: static
static: static-linux cross-mac cross-win cross-arm ## create all static packages

.PHONY: static-linux
static-linux: BUILD_DIR=build/linux
static-linux: static-cli static-engine static-buildx-plugin ## create tgz
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker
	cp $(CLI_DIR)/build/docker $(BUILD_DIR)/docker/

	# docker engine binaries
	for f in dockerd containerd ctr containerd-shim containerd-shim-runc-v2 docker-init docker-proxy runc; do \
		cp -L $(ENGINE_DIR)/bundles/binary-daemon/$$f $(BUILD_DIR)/docker/$$f; \
	done
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-$(GEN_STATIC_VER).tgz docker
	$(RM) -r $(BUILD_DIR)/docker

	# extra binaries for running rootless
	mkdir -p $(BUILD_DIR)/docker-rootless-extras
	for f in rootlesskit rootlesskit-docker-proxy dockerd-rootless.sh dockerd-rootless-setuptool.sh vpnkit; do \
		if [ -f $(ENGINE_DIR)/bundles/binary-daemon/$$f ]; then \
			cp -L $(ENGINE_DIR)/bundles/binary-daemon/$$f $(BUILD_DIR)/docker-rootless-extras/$$f; \
		fi \
	done
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-rootless-extras-$(GEN_STATIC_VER).tgz docker-rootless-extras
	$(RM) -r $(BUILD_DIR)/docker-rootless-extras

	# docker buildx
	tar -C $(BUILDX_DIR)/bin -c -z -f $(BUILD_DIR)/docker-buildx-plugin-$(DOCKER_BUILDX_REF:v%=%).tgz docker-buildx

.PHONY: hash_files
hash_files:
	@echo "Hashing directory $(DIR_TO_HASH)"
	$(HASH_CMD) "$(DIR_TO_HASH)"

.PHONY: buildx
buildx:
	docker buildx inspect | grep -q 'Driver: docker-container' || docker buildx create --use

.PHONY: cross-mac
cross-mac: buildx
	# docker cli binaries
	cd $(CLI_DIR) && VERSION=$(GEN_STATIC_VER) docker buildx bake --set binary.platform=darwin/amd64,darwin/arm64 binary
	dest=$$PWD/build/mac; cd $(CLI_DIR)/build && for platform in *; do \
		arch=$$(echo $$platform | cut -d_ -f2); \
		mkdir -p $$dest/$$arch/docker; \
		cp $$platform/docker-darwin-* $$dest/$$arch/docker/docker && \
		tar -C $$dest/$$arch -c -z -f $$dest/$$arch/docker-$(GEN_STATIC_VER).tgz docker; \
		$(RM) -r $$dest/$$arch/docker
	done

.PHONY: cross-win
cross-win: BUILD_DIR=build/win/amd64
cross-win: cross-win-engine
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker
	cd $(CLI_DIR) && VERSION=$(GEN_STATIC_VER) docker buildx bake --set binary.platform=windows/amd64 binary
	cp $(CLI_DIR)/build/docker-windows-amd64.exe $(BUILD_DIR)/docker/docker.exe

	# docker engine binaries
	cp $(ENGINE_DIR)/bundles/cross/windows/amd64-daemon/dockerd.exe $(BUILD_DIR)/docker/dockerd.exe
	cp $(ENGINE_DIR)/bundles/cross/windows/amd64-daemon/docker-proxy.exe $(BUILD_DIR)/docker/docker-proxy.exe
	docker run --rm -v $(CURDIR)/$(BUILD_DIR):/v -w /v alpine sh -c 'apk update&&apk add zip&&zip -r docker-$(GEN_STATIC_VER).zip docker'
	$(CHOWN) -R $(shell id -u):$(shell id -g) build

	# clean up temporary directories
	$(RM) -r $(BUILD_DIR)/docker

.PHONY: cross-arm
cross-arm: BUILD_DIR=build/arm
cross-arm: cross-all-cli ## create tgz with linux armhf client only
	mkdir -p $(BUILD_DIR)/docker
	cp $(CLI_DIR)/build/docker-linux-arm $(BUILD_DIR)/docker/docker
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-$(GEN_STATIC_VER).tgz docker
	$(RM) -r $(BUILD_DIR)/docker

.PHONY: static-cli
static-cli:
	# TODO(thaJeztah) check if CGO_ENABLED variable is correct here
	cd $(CLI_DIR) && VERSION=$(GEN_STATIC_VER) docker buildx bake --set binary.platform=$(TARGETPLATFORM) --set binary.args.CGO_ENABLED=$(CGO_ENABLED) binary

.PHONY: static-engine
static-engine:
	$(MAKE) -C $(ENGINE_DIR) VERSION=$(GEN_STATIC_VER) DOCKER_BUILD_OPTS="$(DOCKER_BUILD_OPTS)" binary

.PHONY: static-buildx-plugin
static-buildx-plugin:
	cd $(BUILDX_DIR) && docker buildx bake --set binaries.platform=$(TARGETPLATFORM) binaries && mv ./bin/buildx ./bin/docker-buildx

.PHONY: cross-all-cli
cross-all-cli:
	$(MAKE) -C $(CLI_DIR) -f docker.Makefile VERSION=$(GEN_STATIC_VER) cross

.PHONY: cross-win-engine
cross-win-engine:
	$(MAKE) -C $(ENGINE_DIR) VERSION=$(GEN_STATIC_VER) DOCKER_CROSSPLATFORMS=windows/amd64 DOCKER_BUILD_OPTS="$(DOCKER_BUILD_OPTS)" cross
