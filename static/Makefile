include ../common.mk

CLI_DIR     = $(realpath $(CURDIR)/../src/github.com/docker/cli)
ENGINE_DIR  = $(realpath $(CURDIR)/../src/github.com/docker/docker)
COMPOSE_DIR = $(realpath $(CURDIR)/../src/github.com/docker/compose)
BUILDX_DIR  = $(realpath $(CURDIR)/../src/github.com/docker/buildx)
SCAN_DIR    = $(realpath $(CURDIR)/../src/github.com/docker/scan-cli-plugin)

CLI_VERSION        = $(shell ./gen-static-ver $(CLI_DIR) $(VERSION))
ENGINE_VERSION     = $(shell ./gen-static-ver $(ENGINE_DIR) $(VERSION))
CONTAINERD_PKG_VER = $(shell ./gen-containerd-ver $(ENGINE_DIR) $(CONTAINERD_VERSION))

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
static-linux: static-cli static-engine static-buildx-plugin static-compose-plugin docker-scan-plugin ## create tgz
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker-cli
	cp $(CLI_DIR)/build/docker $(BUILD_DIR)/docker-cli/
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-cli-$(CLI_VERSION).tgz docker-cli
	$(RM) -r $(BUILD_DIR)/docker-cli

	# docker engine binaries
	mkdir -p $(BUILD_DIR)/docker-engine
	for f in dockerd docker-init docker-proxy; do \
		cp -L $(ENGINE_DIR)/bundles/binary-daemon/$$f $(BUILD_DIR)/docker-engine/$$f; \
	done
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-engine-$(ENGINE_VERSION).tgz docker-engine
	$(RM) -r $(BUILD_DIR)/docker-engine

	# containerd binaries
	mkdir -p $(BUILD_DIR)/containerd
	for f in containerd ctr containerd-shim-runc-v2 runc; do \
		cp -L $(ENGINE_DIR)/bundles/binary-daemon/$$f $(BUILD_DIR)/containerd/$$f; \
	done
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/containerd-$(CONTAINERD_PKG_VER).tgz containerd
	$(RM) -r $(BUILD_DIR)/containerd

	# extra binaries for running rootless
	mkdir -p $(BUILD_DIR)/docker-rootless-extras
	for f in rootlesskit rootlesskit-docker-proxy dockerd-rootless.sh dockerd-rootless-setuptool.sh vpnkit; do \
		if [ -f $(ENGINE_DIR)/bundles/binary-daemon/$$f ]; then \
			cp -L $(ENGINE_DIR)/bundles/binary-daemon/$$f $(BUILD_DIR)/docker-rootless-extras/$$f; \
		fi \
	done
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-rootless-extras-$(ENGINE_VERSION).tgz docker-rootless-extras
	$(RM) -r $(BUILD_DIR)/docker-rootless-extras

	# docker compose
	tar -C $(COMPOSE_DIR)/bin -c -z -f $(BUILD_DIR)/docker-compose-plugin-$(DOCKER_COMPOSE_REF:v%=%).tgz docker-compose

	# docker buildx
	tar -C $(BUILDX_DIR)/bin -c -z -f $(BUILD_DIR)/docker-buildx-plugin-$(DOCKER_BUILDX_REF:v%=%).tgz docker-buildx

	# docker scan
	tar -C $(SCAN_DIR)/bin -c -z -f $(BUILD_DIR)/docker-scan-plugin-$(DOCKER_SCAN_REF:v%=%).tgz docker-scan

.PHONY: hash_files
hash_files:
	@echo "Hashing directory $(DIR_TO_HASH)"
	$(HASH_CMD) "$(DIR_TO_HASH)"

.PHONY: buildx
buildx:
	docker buildx inspect | grep -q 'Driver: docker-container' || docker buildx create --use

.PHONY: cross-mac
cross-mac: cross-mac-amd64 cross-mac-arm64
	@echo "Cross-compiling mac binaries"

.PHONY: cross-mac-amd64
cross-mac-amd64: TARGETPLATFORM=darwin/amd64
cross-mac-amd64: BUILD_DIR=build/mac/amd64
cross-mac-amd64: buildx static-cli static-buildx-plugin static-compose-plugin cross-scan-plugin
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker-cli
	cp -L $(CLI_DIR)/build/docker $(BUILD_DIR)/docker-cli/docker
	tar -C $(BUILD_DIR)/ -c -z -f $(BUILD_DIR)/docker-cli-$(CLI_VERSION).tgz docker-cli
	$(RM) -r $(BUILD_DIR)/docker-cli

	# docker compose
	tar -C $(COMPOSE_DIR)/bin -c -z -f $(BUILD_DIR)/docker-compose-plugin-$(DOCKER_COMPOSE_REF:v%=%).tgz docker-compose

	# docker buildx
	tar -C $(BUILDX_DIR)/bin -c -z -f $(BUILD_DIR)/docker-buildx-plugin-$(DOCKER_BUILDX_REF:v%=%).tgz docker-buildx

	# docker scan
	mkdir -p $(BUILD_DIR)/docker-scan
	cp -L $(SCAN_DIR)/dist/docker-scan_darwin_amd64 $(BUILD_DIR)/docker-scan/docker-scan
	tar -C $(BUILD_DIR)/ -c -z -f $(BUILD_DIR)/docker-scan-plugin-$(DOCKER_SCAN_REF:v%=%).tgz docker-scan
	$(RM) -r $(BUILD_DIR)/docker-scan

.PHONY: cross-mac-arm64
cross-mac-arm64: TARGETPLATFORM=darwin/arm64
cross-mac-arm64: BUILD_DIR=build/mac/arm64
cross-mac-arm64: buildx static-cli static-buildx-plugin static-compose-plugin cross-scan-plugin
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker-cli
	cp -L $(CLI_DIR)/build/docker $(BUILD_DIR)/docker-cli/docker
	tar -C $(BUILD_DIR)/ -c -z -f $(BUILD_DIR)/docker-cli-$(CLI_VERSION).tgz docker-cli
	$(RM) -r $(BUILD_DIR)/docker-cli

	# docker compose
	tar -C $(COMPOSE_DIR)/bin -c -z -f $(BUILD_DIR)/docker-compose-plugin-$(DOCKER_COMPOSE_REF:v%=%).tgz docker-compose

	# docker buildx
	tar -C $(BUILDX_DIR)/bin -c -z -f $(BUILD_DIR)/docker-buildx-plugin-$(DOCKER_BUILDX_REF:v%=%).tgz docker-buildx

	# docker scan
	mkdir -p $(BUILD_DIR)/docker-scan
	cp -L $(SCAN_DIR)/dist/docker-scan_darwin_arm64 $(BUILD_DIR)/docker-scan/docker-scan
	tar -C $(BUILD_DIR)/ -c -z -f $(BUILD_DIR)/docker-scan-plugin-$(DOCKER_SCAN_REF:v%=%).tgz docker-scan
	$(RM) -r $(BUILD_DIR)/docker-scan

.PHONY: cross-win
cross-win: TARGETPLATFORM=windows/amd64
cross-win: EXT=.exe
cross-win: BUILD_DIR=build/win/amd64
cross-win: cross-win-engine static-cli static-buildx-plugin static-compose-plugin cross-scan-plugin
	# docker cli binaries
	mkdir -p $(BUILD_DIR)/docker-cli
	cp -L $(CLI_DIR)/build/docker $(BUILD_DIR)/docker-cli/docker.exe

	# docker engine binaries
	mkdir -p $(BUILD_DIR)/docker-engine
	for f in dockerd.exe docker-proxy.exe; do \
		cp -L $(ENGINE_DIR)/bundles/cross/windows/amd64-daemon/$$f $(BUILD_DIR)/docker-engine/$$f; \
	done

	# docker compose, docker buildx
	mkdir -p $(BUILD_DIR)/docker-compose
	cp $(COMPOSE_DIR)/bin/docker-compose/docker-compose.exe $(BUILD_DIR)/docker-compose/docker-compose.exe

	# docker buildx
	mkdir -p $(BUILD_DIR)/docker-buildx
	cp $(BUILDX_DIR)/bin/docker-buildx/docker-buildx.exe $(BUILD_DIR)/docker-buildx/docker-buildx.exe

	# docker scan
	mkdir -p $(BUILD_DIR)/docker-scan
	cp $(SCAN_DIR)/dist/docker-scan_windows_amd64.exe $(BUILD_DIR)/docker-scan/docker-scan.exe

	docker run --rm -v $(CURDIR)/$(BUILD_DIR):/v -w /v alpine sh -c 'apk add --no-cache zip \
	&& zip -r docker-cli-$(CLI_VERSION).zip docker-cli \
	&& zip -r docker-engine-$(ENGINE_VERSION).zip docker-engine \
	&& zip -r docker-compose-plugin-$(DOCKER_COMPOSE_REF:v%=%).zip docker-compose \
	&& zip -r docker-buildx-plugin-$(DOCKER_BUILDX_REF:v%=%).zip docker-buildx '
	$(CHOWN) -R $(shell id -u):$(shell id -g) build

	# clean up temporary directories
	$(RM) -r $(BUILD_DIR)/docker-cli $(BUILD_DIR)/docker-engine $(BUILD_DIR)/docker-compose $(BUILD_DIR)/docker-buildx $(BUILD_DIR)/docker-scan

.PHONY: cross-arm
cross-arm: BUILD_DIR=build/arm
cross-arm: cross-all-cli ## create tgz with linux armhf client only
	mkdir -p $(BUILD_DIR)/docker-cli
	cp $(CLI_DIR)/build/docker-linux-arm $(BUILD_DIR)/docker-cli/docker
	tar -C $(BUILD_DIR) -c -z -f $(BUILD_DIR)/docker-$(CLI_VERSION).tgz docker-cli
	$(RM) -r $(BUILD_DIR)/docker-cli

.PHONY: static-cli
static-cli:
	# TODO(thaJeztah) check if CGO_ENABLED variable is correct here
	cd $(CLI_DIR) && VERSION=$(CLI_VERSION) docker buildx bake --set binary.platform=$(TARGETPLATFORM) --set binary.args.CGO_ENABLED=$(CGO_ENABLED) binary

.PHONY: static-engine
static-engine:
	$(MAKE) -C $(ENGINE_DIR) VERSION=$(ENGINE_VERSION) DOCKER_BUILD_OPTS="$(DOCKER_BUILD_OPTS)" binary

.PHONY: static-buildx-plugin
static-buildx-plugin:
	cd $(BUILDX_DIR) && docker buildx bake --set binaries.platform=$(TARGETPLATFORM) binaries && mkdir -p ./bin/docker-buildx/ && mv ./bin/buildx$(EXT) ./bin/docker-buildx/docker-buildx$(EXT)

.PHONY: static-compose-plugin
static-compose-plugin:
	$(RM) -r "$(COMPOSE_DIR)"/bin
	docker buildx build "$(COMPOSE_DIR)" \
		--target compose-plugin \
		--platform "$(or $(TARGETPLATFORM),local)" \
		--build-arg GIT_TAG="$(DOCKER_COMPOSE_REF)" \
		--output $(COMPOSE_DIR)/bin/docker-compose/

.PHONY: docker-scan-plugin
docker-scan-plugin:
	# Build the scan-plugin
	# TODO this should be skipped on non-x86 because there's no image for non-x86?
	# TODO change once we support scan-plugin on other architectures
	$(MAKE) -C $(SCAN_DIR) GIT_TAG_NAME="$(DOCKER_SCAN_REF)" build

	# TODO(thaJeztah) upstream Makefile should pass PLATFORM_BINARY
	# Binary is named (e.g.) docker-scan_linux_amd64. Rename it to have something consistent
	mv $(SCAN_DIR)/bin/docker-scan_linux_* $(SCAN_DIR)/bin/docker-scan

	ls -laR $(SCAN_DIR)/bin

.PHONY: cross-scan-plugin
cross-scan-plugin:
	# TODO: Add TARGETPLATFORM support on scan-cli-plugin repo to build efficiently with --platform
	$(MAKE) -C  $(SCAN_DIR) GIT_TAG_NAME="$(DOCKER_SCAN_REF)" cross

	ls -laR $(SCAN_DIR)/dist

.PHONY: cross-all-cli
cross-all-cli:
	$(MAKE) -C $(CLI_DIR) -f docker.Makefile VERSION=$(CLI_VERSION) cross

.PHONY: cross-win-engine
cross-win-engine:
	$(MAKE) -C $(ENGINE_DIR) VERSION=$(ENGINE_VERSION) DOCKER_CROSSPLATFORMS=windows/amd64 DOCKER_BUILD_OPTS="$(DOCKER_BUILD_OPTS)" cross
