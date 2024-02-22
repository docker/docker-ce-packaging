# syntax=docker/dockerfile:1

ARG GO_IMAGE
ARG DISTRO=rhel
ARG SUITE=9
ARG BUILD_IMAGE=registry.access.redhat.com/ubi9/ubi

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE} AS subscribed-image
ARG RH_USER
ARG RH_PASS
RUN rm /etc/rhsm-host
RUN subscription-manager register --username=$RH_USER --password=$RH_PASS
RUN subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
# RUN dnf config-manager --set-enabled codeready-builder-for-rhel-9-$(arch)-rpms

FROM subscribed-image

ENV GOPROXY=https://proxy.golang.org|direct
ENV GO111MODULE=off
ENV GOPATH=/go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH 1
ENV DOCKER_BUILDTAGS exclude_graphdriver_btrfs
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}

RUN dnf install -y rpm-build rpmlint
COPY --link SPECS /root/rpmbuild/SPECS
RUN dnf builddep -y /root/rpmbuild/SPECS/*.spec
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
