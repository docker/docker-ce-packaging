ARG GO_IMAGE
ARG DISTRO=centos
ARG SUITE=7
ARG BUILD_IMAGE=${DISTRO}:${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}
ENV GOPROXY=direct
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

# Use recent Git version
ARG GIT_VERSION="2.30.0"
RUN yum install -y \
    curl-devel \
    expat-devel \
    gettext-devel \
    openssl-devel \
    perl-CPAN \
    perl-devel \
    wget \
    zlib-devel \
  && yum --setopt=group_package_types=mandatory,default,optional groupinstall -y "Development Tools" \
  && wget https://github.com/git/git/archive/v${GIT_VERSION}.tar.gz -O git.tar.gz \
  && tar -zxf git.tar.gz \
  && cd git-* \
  && make prefix=/usr/local all \
  && make prefix=/usr/local install \
  && rm -rf /git* \
  && git --version

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
  fi

COPY --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
