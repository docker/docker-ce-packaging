include common.mk

# Taken from: https://www.cmcrossroads.com/article/printing-value-makefile-variable
print-%  : ; @echo $($*)

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean-src
clean-src:
	[ ! -d src ] || $(CHOWN) -R $(shell id -u):$(shell id -g) src
	$(RM) -r src

.PHONY: src
src: src/github.com/docker/cli src/github.com/docker/docker src/github.com/docker/buildx src/github.com/docker/compose src/github.com/docker/scan-cli-plugin ## clone source

ifdef CLI_DIR
src/github.com/docker/cli:
	mkdir -p "$(@D)"
	cp -r "$(CLI_DIR)" $@
else
src/github.com/docker/cli:
	git init $@
	git -C $@ remote add origin "$(DOCKER_CLI_REPO)"
endif

ifdef ENGINE_DIR
src/github.com/docker/docker:
	mkdir -p "$(@D)"
	cp -r "$(ENGINE_DIR)" $@
else
src/github.com/docker/docker:
	git init $@
	git -C $@ remote add origin "$(DOCKER_ENGINE_REPO)"
endif

src/github.com/docker/buildx:
	git init $@
	git -C $@ remote add origin "$(DOCKER_BUILDX_REPO)"

src/github.com/docker/compose:
	git init $@
	git -C $@ remote add origin "$(DOCKER_COMPOSE_REPO)"

src/github.com/docker/scan-cli-plugin:
	git init $@
	git -C $@ remote add origin "$(DOCKER_SCAN_REPO)"


.PHONY: checkout-cli
checkout-cli: src/github.com/docker/cli
	./scripts/checkout.sh src/github.com/docker/cli "$(DOCKER_CLI_REF)"

.PHONY: checkout-docker
checkout-docker: src/github.com/docker/docker
	./scripts/checkout.sh src/github.com/docker/docker "$(DOCKER_ENGINE_REF)"

.PHONY: checkout-buildx
checkout-buildx: src/github.com/docker/buildx
	./scripts/checkout.sh src/github.com/docker/buildx "$(DOCKER_BUILDX_REF)"

.PHONY: checkout-compose
checkout-compose: src/github.com/docker/compose
	./scripts/checkout.sh src/github.com/docker/compose "$(DOCKER_COMPOSE_REF)"

.PHONY: checkout-scan-cli-plugin
checkout-scan-cli-plugin: src/github.com/docker/scan-cli-plugin
	./scripts/checkout.sh src/github.com/docker/scan-cli-plugin "$(DOCKER_SCAN_REF)"

.PHONY: checkout
checkout: checkout-cli checkout-docker checkout-buildx checkout-compose checkout-scan-cli-plugin ## checkout source at the given reference(s)

.PHONY: clean
clean: clean-src ## remove build artifacts
	$(MAKE) -C rpm clean
	$(MAKE) -C deb clean
	$(MAKE) -C static clean

.PHONY: deb rpm
deb rpm: checkout ## build rpm/deb packages
	$(MAKE) -C $@ $@

.PHONY: centos-% fedora-% rhel-%
centos-% fedora-% rhel-%: checkout ## build rpm packages for the specified distro
	$(MAKE) -C rpm $@

.PHONY: debian-% raspbian-% ubuntu-%
debian-% raspbian-% ubuntu-%: checkout ## build deb packages for the specified distro
	$(MAKE) -C deb $@


.PHONY: static
static: checkout ## build static package
	$(MAKE) -C static build

.PHONY: verify
verify: ## verify installation of packages
# to verify using packages from staging, use: make VERIFY_PACKAGE_REPO=stage IMAGE=ubuntu:focal verify
	docker run $(VERIFY_PLATFORM) --rm -i \
		-v "$$(pwd):/v" \
		-e DEBIAN_FRONTEND=noninteractive \
		-e PACKAGE_REPO=$(VERIFY_PACKAGE_REPO) \
		-w /v \
		$(IMAGE) ./verify
