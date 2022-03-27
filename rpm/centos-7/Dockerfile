ARG GO_IMAGE
ARG DISTRO=centos
ARG SUITE=7
ARG BUILD_IMAGE=${DISTRO}:${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}

# Using goproxy instead of "direct" to work around an issue in go mod
# not working with older git versions (default version on CentOS 7 is
# git 1.8), see https://github.com/golang/go/issues/38373, and
# https://github.com/docker/docker-ce-packaging/pull/631#issuecomment-1059363763
ENV GOPROXY=https://proxy.golang.org
ENV GO111MODULE=off
ENV GOPATH=/go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH 1
ENV DOCKER_BUILDTAGS seccomp selinux
ENV RUNC_BUILDTAGS seccomp selinux
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}

# In aarch64 (arm64) images, the altarch repo is specified as repository, but
# failing, so replace the URL.
RUN if [ -f /etc/yum.repos.d/CentOS-Sources.repo ]; then sed -i 's/altarch/centos/g' /etc/yum.repos.d/CentOS-Sources.repo; fi
RUN yum install -y rpm-build rpmlint
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
