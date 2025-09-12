# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:latest
ARG DISTRO=fedora
ARG SUITE=43
ARG BUILD_IMAGE=${DISTRO}:${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}
ENV GOPROXY=https://proxy.golang.org|direct
ENV GO111MODULE=on
ENV GOPATH=/go
ENV GOTOOLCHAIN=local
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH=1
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}
RUN dnf install -y rpm-build dnf-plugins-core
# FIXME(thaJeztah): workaround for building on Fedora 41 and up on arm64
#
# This is the equivalent of https://github.com/docker/containerd-packaging/pull/390
# for containerd packages, but unlike for containerd packages, we currently do
# not run into this issue when building docker-ce packages. We're installing
# this as a precaution, but perhaps it's not needed.
#
# go1.21 and up have a patch that enforces the use of ld.gold to work around
# a bug in GNU binutils. See;
# - https://github.com/golang/go/issues/22040.
# - https://github.com/golang/go/commit/cd77738198ffe0c4a1db58352c89f9b2d2a4e85e
#
# Fedora 41 and up has a fixed version of binutils, and no longer requires that
# patch, but may fail without ld.gold installed;
#
#   /usr/bin/gcc -Wl,-z,now -Wl,-z,nocopyreloc -fuse-ld=gold -o $WORK/b001/exe/a.out -rdynamic /tmp/go-link-1738353519/go.o /tmp/go-link-1738353519/000000.o /tmp/go-link-1738353519/000001.o /tmp/go-link-1738353519/000002.o /tmp/go-link-1738353519/000003.o /tmp/go-link-1738353519/000004.o /tmp/go-link-1738353519/000005.o /tmp/go-link-1738353519/000006.o /tmp/go-link-1738353519/000007.o /tmp/go-link-1738353519/000008.o /tmp/go-link-1738353519/000009.o /tmp/go-link-1738353519/000010.o /tmp/go-link-1738353519/000011.o /tmp/go-link-1738353519/000012.o /tmp/go-link-1738353519/000013.o /tmp/go-link-1738353519/000014.o /tmp/go-link-1738353519/000015.o /tmp/go-link-1738353519/000016.o /tmp/go-link-1738353519/000017.o /tmp/go-link-1738353519/000018.o /tmp/go-link-1738353519/000019.o /tmp/go-link-1738353519/000020.o /tmp/go-link-1738353519/000021.o /tmp/go-link-1738353519/000022.o /tmp/go-link-1738353519/000023.o /tmp/go-link-1738353519/000024.o -O2 -g -lresolv -O2 -g -lpthread -O2 -g -ldl -O2 -g
#   collect2: fatal error: cannot find 'ld'
#
# Fedora's build of Go carries a patch for that, but it's not (yet) in upstream;
# - https://src.fedoraproject.org/rpms/golang/blob/a867bd88a656c1d6e91e7b18bab696dc3fcf1e77/f/0006-Default-to-ld.bfd-on-ARM64.patch
# - https://src.fedoraproject.org/rpms/golang/c/a867bd88a656c1d6e91e7b18bab696dc3fcf1e77?branch=rawhide
#
# As a workaround; install binutils-gold
RUN if [ "$(rpm --query --queryformat='%{ARCH}' rpm)" = 'aarch64' ] && ! command -v ld.gold; then dnf -y install binutils-gold; fi

COPY --link SPECS /root/rpmbuild/SPECS
RUN dnf builddep -y /root/rpmbuild/SPECS/*.spec
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
