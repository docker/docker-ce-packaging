ARG GO_IMAGE
ARG DISTRO=centos
ARG SUITE=8
ARG BUILD_IMAGE=quay.io/centos/${DISTRO}:stream${SUITE}

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE}
ENV GOPROXY=direct
ENV GO111MODULE=off
ENV GOPATH=/go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH 1
ENV DOCKER_BUILDTAGS exclude_graphdriver_btrfs seccomp
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}

# In aarch64 (arm64) images, the altarch repo is specified as repository, but
# failing, so replace the URL.
RUN if [ -f /etc/yum.repos.d/CentOS-Stream-Sources.repo ]; then sed -i 's/altarch/centos/g' /etc/yum.repos.d/CentOS-Stream-Sources.repo; fi

RUN if [ -f /etc/yum.repos.d/CentOS-Stream-PowerTools.repo ]; then sed -i 's/enabled=0/enabled=1/g' /etc/yum.repos.d/CentOS-Stream-PowerTools.repo; fi

# RHEL8 / CentOS 8 changed behavior and no longer "rpm --import" or
# "rpmkeys --import"as part of rpm package's %post scriplet. See
# https://forums.centos.org/viewtopic.php?f=54&t=72574, and
# https://access.redhat.com/solutions/3720351
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
RUN dnf install -y rpm-build rpmlint dnf-plugins-core
COPY SPECS /root/rpmbuild/SPECS

# TODO change once we support scan-plugin on other architectures
RUN \
  if [ "$(uname -m)" = "x86_64" ]; then \
    dnf builddep --define '_without_btrfs 1' -y /root/rpmbuild/SPECS/*.spec; \
  else \
    dnf builddep --define '_without_btrfs 1' -y /root/rpmbuild/SPECS/docker-c*.spec; \
    dnf builddep --define '_without_btrfs 1' -y /root/rpmbuild/SPECS/docker-b*.spec; \
  fi

COPY --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
