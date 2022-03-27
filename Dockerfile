# syntax=docker/dockerfile:1

# common
ARG VERSION="0.0.1-dev"
ARG DEFAULT_PRODUCT_LICENSE="Community Engine"
ARG PACKAGER_NAME
ARG PLATFORM="Docker Engine - Community"

# go
ARG GO_IMAGE="golang"
ARG GO_VERSION="1.17.8"
ARG GO_IMAGE_VARIANT="bullseye"

# pkg matrix
ARG PKG_TYPE="deb"
ARG PKG_DISTRO="debian"
ARG PKG_SUITE="bullseye"
ARG BUILD_IMAGE="debian"
ARG BUILD_IMAGE_VERSION="bullseye"

# deb specific
ARG EPOCH=5

# projects
ARG DOCKER_CLI_REPO="https://github.com/docker/cli.git"
ARG DOCKER_ENGINE_REPO="https://github.com/docker/docker.git"
ARG DOCKER_SCAN_REPO="https://github.com/docker/scan-cli-plugin.git"
ARG DOCKER_COMPOSE_REPO="https://github.com/docker/compose.git"
ARG DOCKER_BUILDX_REPO="https://github.com/docker/buildx.git"
ARG REF="HEAD"
ARG DOCKER_CLI_REF="${DOCKER_CLI_REF:-$REF}"
ARG DOCKER_ENGINE_REF="${DOCKER_ENGINE_REF:-$REF}"
ARG DOCKER_SCAN_REF="v0.17.0"
ARG DOCKER_COMPOSE_REF="v2.3.4"
ARG DOCKER_BUILDX_REF="v0.8.1"

FROM --platform=$BUILDPLATFORM alpine AS src
RUN apk --update --no-cache add bash coreutils curl git tar
WORKDIR /src

FROM src AS src-cli
ARG DOCKER_CLI_REPO
ARG DOCKER_CLI_REF
RUN git clone $DOCKER_CLI_REPO . && git reset --hard $DOCKER_CLI_REF

FROM src AS tgz-cli
COPY --from=src-cli /src /cli
RUN mkdir /out && tar -C / -c -z -f /out/cli.tgz --exclude .git cli

FROM src AS src-engine
ARG DOCKER_ENGINE_REPO
ARG DOCKER_ENGINE_REF
RUN git clone $DOCKER_ENGINE_REPO . && git reset --hard $DOCKER_ENGINE_REF

FROM src AS tgz-engine
COPY --from=src-engine /src /engine
RUN mkdir /out && tar -C / -c -z -f /out/engine.tgz --exclude .git engine

FROM src AS src-scan
ARG DOCKER_SCAN_REPO
ARG DOCKER_SCAN_REF
RUN git clone $DOCKER_SCAN_REPO . && git reset --hard $DOCKER_SCAN_REF

FROM src AS tgz-scan
COPY --from=src-scan /src /scan-cli-plugin
RUN mkdir /out && tar -C / -c -z -f /out/scan-cli-plugin.tgz --exclude .git scan-cli-plugin

FROM src AS src-compose
ARG DOCKER_COMPOSE_REPO
ARG DOCKER_COMPOSE_REF
RUN git clone $DOCKER_COMPOSE_REPO . && git reset --hard $DOCKER_COMPOSE_REF

FROM src AS tgz-compose
COPY --from=src-compose /src /compose
RUN mkdir /out && tar -C / -c -z -f /out/compose.tgz --exclude .git compose

FROM src AS src-buildx
ARG DOCKER_BUILDX_REPO
ARG DOCKER_BUILDX_REF
RUN git clone $DOCKER_BUILDX_REPO . && git reset --hard $DOCKER_BUILDX_REF

FROM src AS tgz-buildx
COPY --from=src-buildx /src /buildx
RUN mkdir /out && tar -C / -c -z -f /out/buildx.tgz --exclude .git buildx

FROM src AS deb-ver
ARG VERSION
COPY deb/gen-deb-ver /usr/local/bin/gen-deb-ver
COPY --from=src-cli /src /src/cli
COPY --from=src-engine /src /src/engine
COPY --from=src-scan /src /src/scan
RUN <<EOT
mkdir /out
echo $(date -u -d "@${SOURCE_DATE_EPOCH:-$(date +%s)}" --rfc-3339 ns 2> /dev/null | sed -e 's/ /T/') > /out/buildtime
echo $(cd /src/cli && git rev-parse --short HEAD) > /out/cli_commit
echo $(cd /src/engine && git rev-parse --short HEAD) > /out/engine_commit
echo $(cd /src/scan && git rev-parse --short HEAD) > /out/scan_commit
echo $(gen-deb-ver /src/cli "$VERSION") > /out/version
EOT

FROM ${GO_IMAGE}:${GO_VERSION}-${GO_IMAGE_VARIANT} AS go
FROM ${BUILD_IMAGE}:${BUILD_IMAGE_VERSION} AS build-base-deb
ARG DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install -y curl devscripts equivs git
ENV GOPROXY="direct"
ENV GO111MODULE="off"
ENV GOPATH="/go"
ENV PATH="$PATH:/usr/local/go/bin:$GOPATH/bin"
ARG PKG_DISTRO
ARG PKG_SUITE
RUN <<EOT
case "$PKG_DISTRO-$PKG_SUITE" in
  ubuntu-focal|ubuntu-hirsute|ubuntu-impish|ubuntu-jammy)
    if [ "$(dpkg-divert --truename /usr/bin/man)" = "/usr/bin/man.REAL" ]; then
      rm -f /usr/bin/man
      dpkg-divert --quiet --remove --rename /usr/bin/man
    fi
  ;;
esac
EOT

FROM build-base-deb AS build-base-debian-bullseye
FROM build-base-deb AS build-base-debian-buster
FROM build-base-deb AS build-base-raspbian-bullseye
FROM build-base-deb AS build-base-raspbian-buster
FROM build-base-deb AS build-base-ubuntu-bionic
FROM build-base-deb AS build-base-ubuntu-focal
FROM build-base-deb AS build-base-ubuntu-hirsute
FROM build-base-deb AS build-base-ubuntu-impish
FROM build-base-deb AS build-base-ubuntu-jammy

FROM build-base-deb AS build-deb
COPY deb/common /root/build-deb/debian
RUN apt-get update && mk-build-deps -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y" -i /root/build-deb/debian/control
WORKDIR /root/build-deb
COPY deb/build-deb /root/build-deb/build-deb
ARG DEFAULT_PRODUCT_LICENSE
ARG PACKAGER_NAME
ARG PLATFORM
ARG EPOCH
ARG PKG_DISTRO
ARG DISTRO=${PKG_DISTRO}
ARG PKG_SUITE
ARG SUITE=${PKG_SUITE}
ARG DOCKER_SCAN_REF
ARG SCAN_VERSION=$DOCKER_SCAN_REF
ARG DOCKER_COMPOSE_REF
ARG COMPOSE_VERSION=$DOCKER_COMPOSE_REF
ARG DOCKER_BUILDX_REF
ARG BUILDX_VERSION=$DOCKER_BUILDX_REF
ENV DOCKER_BUILDTAGS="apparmor seccomp selinux"
ENV RUNC_BUILDTAGS="apparmor seccomp selinux"
RUN --mount=type=bind,from=go,source=/usr/local/go,target=/usr/local/go \
  --mount=type=bind,from=tgz-cli,source=/out/cli.tgz,target=/sources/cli.tgz \
  --mount=type=bind,from=tgz-engine,source=/out/engine.tgz,target=/sources/engine.tgz \
  --mount=type=bind,from=tgz-scan,source=/out/scan-cli-plugin.tgz,target=/sources/scan-cli-plugin.tgz \
  --mount=type=bind,from=tgz-compose,source=/out/compose.tgz,target=/sources/compose.tgz \
  --mount=type=bind,from=tgz-buildx,source=/out/buildx.tgz,target=/sources/buildx.tgz \
  --mount=type=bind,from=deb-ver,source=/out,target=/deb-ver \
  --mount=type=cache,target=/root/.cache \
  --mount=type=cache,target=/go/pkg/mod <<EOT
find /root/build-deb/debian -type f -exec chmod 644 {} \;
export BUILDTIME=$(cat /deb-ver/buildtime)
export DEB_VERSION=$(cat /deb-ver/version | cut -d" " -f1)
export VERSION=$(cat /deb-ver/version | cut -d" " -f2)
export CLI_GITCOMMIT=$(cat /deb-ver/cli_commit)
export ENGINE_GITCOMMIT=$(cat /deb-ver/engine_commit)
export SCAN_GITCOMMIT=$(cat /deb-ver/scan_commit)
/root/build-deb/build-deb
EOT

FROM build-deb AS build-debian-bullseye
FROM build-deb AS build-debian-buster
FROM build-deb AS build-raspbian-bullseye
FROM build-deb AS build-raspbian-buster
FROM build-deb AS build-ubuntu-bionic
FROM build-deb AS build-ubuntu-focal
FROM build-deb AS build-ubuntu-hirsute
FROM build-deb AS build-ubuntu-impish
FROM build-deb AS build-ubuntu-jammy

FROM build-${PKG_DISTRO}-${PKG_SUITE} AS build

FROM scratch AS release
COPY --from=build /build /
