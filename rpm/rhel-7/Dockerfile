# syntax=docker/dockerfile:1

ARG GO_IMAGE
ARG DISTRO=rhel
ARG SUITE=7
ARG BUILD_IMAGE=dockereng/${DISTRO}:${SUITE}-s390x

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}
ENV GOPROXY=https://proxy.golang.org|direct
ENV GO111MODULE=off
ENV GOPATH=/go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH 1
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}
ENV CC=gcc

# In aarch64 (arm64) images, the altarch repo is specified as repository, but
# failing, so replace the URL.
RUN if [ -f /etc/yum.repos.d/CentOS-Sources.repo ]; then sed -i 's/altarch/centos/g' /etc/yum.repos.d/CentOS-Sources.repo; fi
RUN yum install -y rpm-build rpmlint
COPY --link SPECS /root/rpmbuild/SPECS
RUN yum-builddep -y /root/rpmbuild/SPECS/*.spec
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
