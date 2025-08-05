# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:latest
ARG DISTRO=centos
ARG SUITE=10
ARG BUILD_IMAGE=quay.io/centos/${DISTRO}:stream${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}
ENV GOPROXY=https://proxy.golang.org|direct
ENV GO111MODULE=on
ENV GOPATH=/go
ENV GOTOOLCHAIN=local
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH=1
ENV DOCKER_BUILDTAGS=exclude_graphdriver_btrfs
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}

# RHEL8 / CentOS 8 changed behavior and no longer "rpm --import" or
# "rpmkeys --import"as part of rpm package's %post scriplet. See
# https://forums.centos.org/viewtopic.php?f=54&t=72574, and
# https://access.redhat.com/solutions/3720351
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial-SHA256
RUN dnf install -y rpm-build dnf-plugins-core
RUN dnf config-manager --set-enabled crb

COPY --link SPECS /root/rpmbuild/SPECS
RUN dnf builddep -y /root/rpmbuild/SPECS/*.spec
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
