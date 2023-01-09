ARG GO_IMAGE
ARG DISTRO=centos
ARG SUITE=7
ARG BUILD_IMAGE=${DISTRO}:${SUITE}

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

# In aarch64 (arm64) images, the altarch repo is specified as repository, but
# failing, so replace the URL.
RUN if [ -f /etc/yum.repos.d/CentOS-Sources.repo ]; then sed -i 's/altarch/centos/g' /etc/yum.repos.d/CentOS-Sources.repo; fi
RUN yum install -y rpm-build rpmlint

# Install Linux kernel headers for btrfs support.
# See https://github.com/moby/moby/pull/44761 and https://github.com/moby/moby/pull/44762,
# See https://www.kernel.org/doc/Documentation/kbuild/headers_install.txt
RUN yum install -y make gcc \
 && curl -fsSL -O https://github.com/torvalds/linux/archive/refs/tags/v4.12.tar.gz \
 && tar -xvzf ./v4.12.tar.gz \
 && rm v4.12.tar.gz \
 && cd linux-4.12/ \
 && make headers_install ARCH=arm64 INSTALL_HDR_PATH=/usr

COPY SPECS /root/rpmbuild/SPECS

# TODO change once we support scan-plugin on other architectures
RUN \
  if [ "$(uname -m)" = "x86_64" ]; then \
    yum-builddep -y /root/rpmbuild/SPECS/*.spec; \
  else \
    yum-builddep -y /root/rpmbuild/SPECS/docker-c*.spec; \
    yum-builddep -y /root/rpmbuild/SPECS/docker-b*.spec; \
  fi

COPY --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
