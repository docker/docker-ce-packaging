ARG GO_IMAGE
ARG DISTRO=ubuntu
ARG SUITE=bionic
ARG BUILD_IMAGE=${DISTRO}:${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE} AS build-base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl devscripts equivs git
WORKDIR /root/build-deb
ARG COMMON_FILES
COPY ${COMMON_FILES} ./debian
RUN mk-build-deps -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y" -i /root/build-deb/debian/control
ARG VERSION
ARG DOCKER_GITCOMMIT
ARG PLATFORM
ENV VERSION=${VERSION}
ENV DOCKER_GITCOMMIT=${DOCKER_GITCOMMIT}
ENV PLATFORM=${PLATFORM}

# Golang base stage to build go binaries
# This stage is based on the given distro, and sets Golang-specific env-vars
FROM build-base AS golang-build
ENV GOPROXY=direct
ENV GO111MODULE=off
ENV GOPATH /go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
COPY --from=golang /usr/local/go /usr/local/go

# Build the manpages
FROM golang-build AS manpages-build
ENV DISABLE_WARN_OUTSIDE_CONTAINER=1
ADD sources/cli.tgz /go/src/github.com/docker/
WORKDIR /go/src/github.com/docker/cli
RUN LDFLAGS='' make manpages

# Build the cli
# TODO: the build scripts from upstream, names the binary with the architecture
# (and version?) in its name, and creates a "docker" symlink. We don't need those,
# so either update the upstream scripts, or just execute the right commands ourselves.
FROM golang-build AS cli-build
ENV DISABLE_WARN_OUTSIDE_CONTAINER=1

# TODO: why are we creating a `tgz` for the sources if we can just add a directory?
ADD sources/cli.tgz /go/src/github.com/docker/
WORKDIR /go/src/github.com/docker/cli
RUN LDFLAGS='' make dynbinary && mv build/docker-* /usr/local/bin/docker
RUN docker --version

# Build the plugins
FROM golang-build AS plugins-build
ADD sources/plugin-installers.tgz /build
WORKDIR /build/
# TODO each plugin does a git clone before building and installing. The clone
# is platform independent, so we should have a stage that does the clone in a
# generic base-image, so that we can reuse that step. Alternatively, we should
# clone the plugin sources on the host, not as part of the Dockerfile
RUN for installer in plugins/*.installer; do \
        LDFLAGS='' bash ${installer} build; \
    done

# TODO dirty trick because plugins are each installed in their own go source directory
RUN mkdir -p /build/bin/ && cp /go/src/github.com/*/*/bin/* /build/bin/

# Build the daemon and dependencies
# TODO: the build scripts from upstream, names the binary with the architecture
# in its name, and creates a "dockerd" symlink. We don't need those, so either
# update the upstream scripts, or just execute the right commands ourselves.
FROM golang-build AS engine-build
ENV DOCKER_BUILDTAGS="apparmor seccomp selinux"
ENV RUNC_BUILDTAGS="apparmor seccomp selinux"

# TODO: why are we creating a `tgz` for the sources if we can just add a directory?
# this would also solve having to do a "mv" below.
ADD sources/engine.tgz /go/src/github.com/docker/
RUN mv /go/src/github.com/docker/engine /go/src/github.com/docker/docker
WORKDIR /go/src/github.com/docker/docker
RUN PRODUCT=docker ./hack/make.sh dynbinary
RUN TMP_GOPATH="/go" hack/dockerfile/install/install.sh tini
RUN TMP_GOPATH="/go" hack/dockerfile/install/install.sh proxy dynamic
RUN bundles/dynbinary-daemon/dockerd --version

FROM scratch AS completion
COPY --from=manpages-build /go/src/github.com/docker/cli/contrib/completion /completion

FROM scratch AS manpages
COPY --from=manpages-build /go/src/github.com/docker/cli/man/man1 /man/man1

FROM scratch AS plugins
COPY --from=plugins-build /build/bin/. /cli-plugins/

FROM scratch AS cli
COPY --from=cli-build /usr/local/bin/docker /bin/

FROM scratch AS engine
COPY --from=engine-build /go/src/github.com/docker/docker/bundles/dynbinary-daemon/. /bin/

# Build this stage with
# make UBUNTU_VERSIONS=ubuntu-bionic DEBIAN_VERSIONS="" CLI_DIR=$GOPATH/src/github.com/docker/cli ENGINE_DIR=$GOPATH/src/github.com/docker/docker deb
#
# Collect all the artefacts. Note that we didn't build containerd or runc, so
# we can't run the daemon. We can try the cli against a daemon on the host though;
# docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock debbuild-ubuntu-bionic/x86_64
#
# This stage is based on build-base, so contains the ~/build-deb directory, which
# we probably should clean up.
FROM build-base AS final
COPY --from=completion  /.      /build/
COPY --from=manpages    /.      /build/
COPY --from=plugins     /.      /root/.docker/cli-plugins/
COPY --from=cli         /bin/.  /usr/local/bin/
COPY --from=engine      /bin/.  /usr/local/bin/
RUN echo '{"experimental":"enabled", "debug": true}' > /root/.docker/config.json \
 && docker --help
WORKDIR /build/

# Stage to collect all the binaries, which could be used with `--output type=local,dsc=build
#
# Build this stage with
# make UBUNTU_VERSIONS=ubuntu-bionic DEBIAN_VERSIONS="" CLI_DIR=$GOPATH/src/github.com/docker/cli ENGINE_DIR=$GOPATH/src/github.com/docker/docker binaries
FROM scratch AS binaries
COPY --from=completion  /. /
COPY --from=manpages    /. /
COPY --from=plugins     /. /
COPY --from=cli         /. /
COPY --from=engine      /. /

FROM build-base AS deb
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}
COPY build-deb .
COPY sources/distribution_based_engine.json docker.service docker.socket engine.image /go/src/github.com/docker/
ENTRYPOINT ["/root/build-deb/build-deb"]
