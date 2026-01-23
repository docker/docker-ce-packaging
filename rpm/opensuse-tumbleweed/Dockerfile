# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:latest
ARG DISTRO=opensuse
ARG SUITE=tumbleweed
ARG BUILD_IMAGE=registry.opensuse.org/${DISTRO}/${SUITE}

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
RUN zypper install -y rpm-build

COPY --link SPECS /root/rpmbuild/SPECS
RUN zypper -n install -y --force-resolution $(rpmspec -q --buildrequires /root/rpmbuild/SPECS/*.spec)
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
