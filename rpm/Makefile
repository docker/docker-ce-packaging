include ../common.mk

PLUGINS_DIR=$(realpath $(CURDIR)/../plugins)
GO_BASE_IMAGE=golang
GO_IMAGE?=$(GO_BASE_IMAGE):$(GO_VERSION)-bookworm
GEN_RPM_VER=$(shell ./gen-rpm-ver $(realpath $(CURDIR)/../src/github.com/docker/cli) "$(VERSION)")
GEN_BUILDX_RPM_VER=$(shell ./gen-rpm-ver $(realpath $(CURDIR)/../src/github.com/docker/buildx) "$(DOCKER_BUILDX_REF)")
GEN_COMPOSE_RPM_VER=$(shell ./gen-rpm-ver $(realpath $(CURDIR)/../src/github.com/docker/compose) "$(DOCKER_COMPOSE_REF)")
GEN_MODEL_RPM_VER=$(shell ./gen-rpm-ver $(realpath $(CURDIR)/../src/github.com/docker/model-cli) "$(DOCKER_MODEL_REF)")
CLI_GITCOMMIT?=$(shell cd $(realpath $(CURDIR)/../src/github.com/docker/cli) && git rev-parse --short HEAD)
ENGINE_GITCOMMIT?=$(shell cd $(realpath $(CURDIR)/../src/github.com/docker/docker) && git rev-parse --short HEAD)
BUILDX_GITCOMMIT?=$(shell cd $(realpath $(CURDIR)/../src/github.com/docker/buildx) && git rev-parse --short HEAD)

ifdef RH_USER
	RH_FLAGS=--secret id=rh-user,env=RH_USER --secret id=rh-pass,env=RH_PASS
endif
ifdef BUILD_IMAGE
	BUILD_IMAGE_FLAG=--build-arg $(BUILD_IMAGE)
endif
BUILD?=DOCKER_BUILDKIT=1 \
	docker build \
	$(RH_FLAGS) \
	$(BUILD_IMAGE_FLAG) \
	--build-arg GO_IMAGE=$(GO_IMAGE) \
	-t rpmbuild-$@/$(ARCH) \
	--platform linux/$(ARCH) \
	-f $@/Dockerfile \
	.


SPEC_FILES?=docker-ce.spec docker-ce-cli.spec docker-ce-rootless-extras.spec docker-buildx-plugin.spec docker-compose-plugin.spec docker-model-plugin.spec

SPECS?=$(addprefix SPECS/, $(SPEC_FILES))
RPMBUILD_FLAGS?=-ba\
	--define '_gitcommit_cli $(CLI_GITCOMMIT)' \
	--define '_gitcommit_engine $(ENGINE_GITCOMMIT)' \
	--define '_release $(word 2,$(GEN_RPM_VER))' \
	--define '_version $(word 1,$(GEN_RPM_VER))' \
	--define '_origversion $(word 4, $(GEN_RPM_VER))' \
	--define '_buildx_rpm_version $(word 1,$(GEN_BUILDX_RPM_VER))' \
	--define '_buildx_version $(word 4,$(GEN_BUILDX_RPM_VER))' \
	--define '_buildx_gitcommit $(BUILDX_GITCOMMIT)' \
	--define '_compose_rpm_version $(word 1,$(GEN_COMPOSE_RPM_VER))' \
	--define '_compose_version $(word 4,$(GEN_COMPOSE_RPM_VER))' \
	--define '_model_rpm_version $(word 1,$(GEN_MODEL_RPM_VER))' \
	--define '_model_version $(word 4,$(GEN_MODEL_RPM_VER))' \
	$(RPMBUILD_EXTRA_FLAGS) \
	$(SPECS)

# Additional flags may be necessary at some point
RUN_FLAGS=

# FIXME(thaJeztah): disabling seccomp to handle (ppc64le) tar "chown / chmod"
# failing when running in a Fedora 40 container on a Debian bookworm host;
# see https://github.com/docker/docker-ce-packaging/issues/1012 and
# https://github.com/docker/docker-ce-packaging/pull/1006#issuecomment-2006878743
RUN?=docker run --rm \
	--security-opt seccomp=unconfined \
	--platform linux/$(ARCH) \
	-e PLATFORM \
	-v $(CURDIR)/rpmbuild/SOURCES:/root/rpmbuild/SOURCES:ro \
	-v $(CURDIR)/rpmbuild/$@/RPMS:/root/rpmbuild/RPMS \
	-v $(CURDIR)/rpmbuild/$@/SRPMS:/root/rpmbuild/SRPMS \
	$(RUN_FLAGS) \
	rpmbuild-$@/$(ARCH) $(RPMBUILD_FLAGS)

FEDORA_RELEASES ?= fedora-41 fedora-42 fedora-43
CENTOS_RELEASES ?= centos-9 centos-10
RHEL_RELEASES ?= rhel-8 rhel-9 rhel-10

DISTROS := $(FEDORA_RELEASES) $(CENTOS_RELEASES) $(RHEL_RELEASES)
BUNDLES := $(patsubst %,rpmbuild/bundles-ce-%-$(DPKG_ARCH).tar.gz,$(DISTROS))

.PHONY: help
help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	[ ! -d rpmbuild ] || $(CHOWN) -R $(shell id -u):$(shell id -g) rpmbuild
	$(RM) -r rpmbuild/
	-docker builder prune -f --filter until=24h

.PHONY: rpm
rpm: fedora centos ## build all rpm packages

.PHONY: fedora
fedora: $(FEDORA_RELEASES) ## build all fedora rpm packages

.PHONY: centos
centos: $(CENTOS_RELEASES) ## build all centos rpm packages

.PHONY: rhel
rhel: $(RHEL_RELEASES) ## build all rhel rpm packages
# The nftables-devel package is only available in RHEL CRB. For now, build
# with tag "no_libnftables", so dockerd will exec the nft tool, and this
# package is not required. Note that this '--define' is also hard-coded in
# each of the rhel-*/Dockerfile files.
$(RHEL_RELEASES): RPMBUILD_EXTRA_FLAGS += --define '_no_libnftables true'

.PHONY: $(DISTROS)
$(DISTROS): sources
	@echo "== Building packages for $@ =="
	mkdir -p "rpmbuild/$@"
	$(BUILD)
	$(RUN)
	$(CHOWN) -R $(shell id -u):$(shell id -g) "rpmbuild/$@"

.PHONY: sources
sources: rpmbuild/SOURCES/engine.tgz rpmbuild/SOURCES/cli.tgz rpmbuild/SOURCES/buildx.tgz rpmbuild/SOURCES/compose.tgz rpmbuild/SOURCES/model.tgz

rpmbuild/SOURCES/engine.tgz:
	mkdir -p $(@D)
	docker run --rm -w /v \
		-v $(realpath $(CURDIR)/../src/github.com/docker/docker):/engine \
		-v $(CURDIR)/$(@D):/v \
		alpine \
		tar -C / -c -z -f /v/engine.tgz --exclude .git engine

rpmbuild/SOURCES/cli.tgz:
	mkdir -p $(@D)
	docker run --rm -w /v \
		-v $(realpath $(CURDIR)/../src/github.com/docker/cli):/cli \
		-v $(CURDIR)/$(@D):/v \
		alpine \
		tar -C / -c -z -f /v/cli.tgz --exclude .git cli

rpmbuild/SOURCES/buildx.tgz:
	mkdir -p $(@D)
	docker run --rm -w /v \
		-v $(realpath $(CURDIR)/../src/github.com/docker/buildx):/buildx \
		-v $(CURDIR)/$(@D):/v \
		alpine \
		tar -C / -c -z -f /v/buildx.tgz --exclude .git buildx

rpmbuild/SOURCES/compose.tgz:
	mkdir -p $(@D)
	docker run --rm -w /v \
		-v $(realpath $(CURDIR)/../src/github.com/docker/compose):/compose \
		-v $(CURDIR)/$(@D):/v \
		alpine \
		tar -C / -c -z -f /v/compose.tgz --exclude .git compose

rpmbuild/SOURCES/model.tgz:
	mkdir -p $(@D)
	docker run --rm -w /v \
		-v $(realpath $(CURDIR)/../src/github.com/docker/model-cli):/model \
		-v $(CURDIR)/$(@D):/v \
		alpine \
		tar -C / -c -z -f /v/model.tgz --exclude .git model

# See ARCHES in common.mk. Could not figure out how to match both distro and arch.
BUNDLES:=$(addsuffix .tar.gz,$(addprefix rpmbuild/bundles-ce-%-,$(ARCHES)))

$(BUNDLES): %
	tar czf $@ --transform="s|^rpmbuild/\(.*\)|bundles/$(VERSION)/build-rpm/\1|" rpmbuild/$*
