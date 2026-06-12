%global debug_package %{nil}

Name: docker-ce
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 3
Source0: engine.tgz
Summary: The open-source application container engine
Group: Tools/Docker
License: Apache-2.0
URL: https://www.docker.com
Vendor: Docker
Packager: Docker <support@docker.com>

Requires: /usr/sbin/groupadd
Requires: docker-ce-cli
Recommends: docker-ce-rootless-extras
Requires: container-selinux
Requires: systemd
Requires: (iptables-nft or iptables)
Requires: nftables
%if %{undefined rhel} || 0%{?rhel} < 9
# Libcgroup is no longer available in RHEL/CentOS >= 9 distros.
%if 0%{?suse_version}
Requires: libcgroup3
%else
Requires: libcgroup
%endif
%endif
Requires: containerd.io >= 1.7.27
Requires: tar
Requires: xz

BuildRequires: bash
BuildRequires: ca-certificates
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: git
BuildRequires: glibc-static
BuildRequires: libtool
%if %{undefined _no_libnftables}
BuildRequires: nftables-devel
%endif
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: pkgconfig(systemd)
BuildRequires: systemd-devel
BuildRequires: tar

# conflicting packages
Conflicts: docker
Conflicts: docker-io
Conflicts: docker-ee

%description
Docker is a product for you to build, ship and run any application as a
lightweight container.

Docker containers are both hardware-agnostic and platform-agnostic. This means
they can run anywhere, from your laptop to the largest cloud compute instance
and everything in between - and they don't require you to use a particular
language, framework or packaging system. That makes them great building blocks
for deploying and scaling web apps, databases, and backend services without
depending on a particular stack or provider.

%prep
%setup -q -c -n src -a 0

%build

export DOCKER_GITCOMMIT=%{_gitcommit_engine}
mkdir -p /go/src/github.com/docker
ln -snf ${RPM_BUILD_DIR}/src/engine /go/src/github.com/docker/docker

pushd ${RPM_BUILD_DIR}/src/engine
TMP_GOPATH="/go" hack/dockerfile/install/install.sh tini

# Determine Go module mode based on file presence
if [ -f vendor.mod ]; then
    GOMOD=off
elif [ -f go.mod ]; then
    GOMOD=on
else
    echo "No go.mod or vendor.mod found in engine directory"
    exit 1
fi
GO111MODULE=$GOMOD VERSION=%{_origversion} PRODUCT=docker hack/make.sh dynbinary
popd

#  build  man-pages
make -C ${RPM_BUILD_DIR}/src/engine/man

%check
ver="$(engine/bundles/dynbinary-daemon/dockerd --version)"; \
    test "$ver" = "Docker version %{_origversion}, build %{_gitcommit_engine}" && echo "PASS: daemon version OK" || (echo "FAIL: daemon version ($ver) did not match" && exit 1)

%install
install -D -p -m 0755 $(readlink -f engine/bundles/dynbinary-daemon/dockerd) ${RPM_BUILD_ROOT}%{_bindir}/dockerd
install -D -p -m 0755 $(readlink -f engine/bundles/dynbinary-daemon/docker-proxy) ${RPM_BUILD_ROOT}%{_bindir}/docker-proxy
install -D -p -m 0755 /usr/local/bin/docker-init ${RPM_BUILD_ROOT}%{_libexecdir}/docker/docker-init

# install systemd scripts
install -D -p -m 0644 engine/contrib/init/systemd/docker.service ${RPM_BUILD_ROOT}%{_unitdir}/docker.service
install -D -p -m 0644 engine/contrib/init/systemd/docker.socket ${RPM_BUILD_ROOT}%{_unitdir}/docker.socket

# install manpages
make -C ${RPM_BUILD_DIR}/src/engine/man DESTDIR=${RPM_BUILD_ROOT} mandir=%{_mandir} install

# install SELinux policy to deny AF_ALG sockets in container domains
install -D -m 644 engine/contrib/selinux/docker-af-alg-deny.cil %{buildroot}%{_datadir}/docker-ce/selinux/docker-af-alg-deny.cil

# create the config directory
mkdir -p ${RPM_BUILD_ROOT}/etc/docker

%files
%{_bindir}/dockerd
%{_bindir}/docker-proxy
%{_libexecdir}/docker/docker-init
%{_unitdir}/docker.service
%{_unitdir}/docker.socket
%{_mandir}/man*/*
%{_datadir}/docker-ce/selinux/docker-af-alg-deny.cil
%dir /etc/docker

%post
%systemd_post docker.service
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi
# Load the AF_ALG deny policy when SELinux is enabled. This may fail on systems
# with SELinux userspace < 3.6, or without container-selinux's container_domain
# attribute, so keep installation non-fatal.
if command -v semodule > /dev/null 2>&1 && selinuxenabled 2>/dev/null; then
    if ! semodule -i %{_datadir}/docker-ce/selinux/docker-af-alg-deny.cil 2>/dev/null; then
        echo "warning: could not load docker-af-alg-deny.cil SELinux policy; AF_ALG SELinux denial is not active" >&2
    fi
fi

%preun
%systemd_preun docker.service docker.socket

%postun
%systemd_postun_with_restart docker.service
if [ "$1" -eq 0 ]; then
    if command -v semodule > /dev/null 2>&1; then
        semodule -r container-af-alg-deny 2>/dev/null || :
    fi
fi

%changelog
