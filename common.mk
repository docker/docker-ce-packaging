ARCH=$(shell uname -m)

# These are the architecture formats as used in release-packaging Jenkinsfile
# This is an ugly chimera, nobody uses this combination of dpkg and uname formats
# Why don't we pick one format and stick with it? Because at the time of writing
# it was deemed too risky/involving too many changes across repos to change architecture
# formats in release-packaging Jenkinsfile. But someone please do it.
# Why do we need to list this here? Because I haven't been able to figure out how
# to do Makefile rules with multiple patterns. (See how it's used in {deb,rpm}/Makefile)
# Adding new architectures or changing the format in release-packaging will prevent make
# from finding the corresponding rule unless this list is updated.
# Or Jenkinsfiles/Makefiles removed (🎵 Gotta have faith-a-faith-a-faith... 🎵)
ARCHES:=amd64 aarch64 armhf armel s390x ppc64le

BUILDTIME=$(shell date -u -d "@$${SOURCE_DATE_EPOCH:-$$(date +%s)}" --rfc-3339 ns 2> /dev/null | sed -e 's/ /T/')
CHOWN:=docker run --rm -v $(CURDIR):/v -w /v alpine chown
DEFAULT_PRODUCT_LICENSE:=Community Engine
PACKAGER_NAME?=
DOCKER_GITCOMMIT:=abcdefg
GO_VERSION:=1.18.3
PLATFORM=Docker Engine - Community
SHELL:=/bin/bash
VERSION?=0.0.1-dev

# DOCKER_CLI_REPO and DOCKER_ENGINE_REPO define the source repositories to clone
# the source from. These can be overridden to build from a fork.
DOCKER_CLI_REPO     ?= https://github.com/docker/cli.git
DOCKER_ENGINE_REPO  ?= https://github.com/docker/docker.git
DOCKER_SCAN_REPO    ?= https://github.com/docker/scan-cli-plugin.git
DOCKER_COMPOSE_REPO ?= https://github.com/docker/compose.git
DOCKER_BUILDX_REPO  ?= https://github.com/docker/buildx.git

# REF can be used to specify the same branch or tag to use for *both* the CLI
# and Engine source code. This can be useful if both the CLI and Engine have a
# release branch with the same name (e.g. "19.03"), or of both repositories have
# tagged a release with the same version.
#
# For other situations, specify DOCKER_CLI_REF and/or DOCKER_ENGINE_REF separately.
REF                ?= HEAD
DOCKER_CLI_REF     ?= $(REF)
DOCKER_ENGINE_REF  ?= $(REF)
DOCKER_SCAN_REF    ?= v0.17.0
DOCKER_COMPOSE_REF ?= v2.6.1
DOCKER_BUILDX_REF  ?= v0.8.2

# Use "stage" to install dependencies from download-stage.docker.com during the
# verify step. Leave empty or use any other value to install from download.docker.com
VERIFY_PACKAGE_REPO ?= staging

# Optional flags like --platform=linux/armhf
VERIFY_PLATFORM ?=

# Export vars as envs
export BUILDTIME
export DEFAULT_PRODUCT_LICENSE
export PACKAGER_NAME
export PLATFORM
export VERSION
export GO_VERSION

export DOCKER_CLI_REPO
export DOCKER_ENGINE_REPO
export DOCKER_SCAN_REPO
export DOCKER_COMPOSE_REPO
export DOCKER_BUILDX_REPO

export REF
export DOCKER_CLI_REF
export DOCKER_ENGINE_REF
export DOCKER_SCAN_REF
export DOCKER_COMPOSE_REF
export DOCKER_BUILDX_REF

# utilities
BOLD := $(shell tput -T linux bold)
RED := $(shell tput -T linux setaf 1)
GREEN := $(shell tput -T linux setaf 2)
YELLOW := $(shell tput -T linux setaf 3)
BLUE := $(shell tput -T linux setaf 4)
PURPLE := $(shell tput -T linux setaf 5)
CYAN := $(shell tput -T linux setaf 6)

RESET := $(shell tput -T linux sgr0)
TITLE := $(BOLD)$(YELLOW)
SUCCESS := $(BOLD)$(GREEN)

define title
    @printf '$(TITLE)$(1)$(RESET)\n'
endef
