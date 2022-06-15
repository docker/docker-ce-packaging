%global debug_package %{nil}

# BTRFS is enabled by default, but can be disabled by defining _without_btrfs
%if %{undefined _with_btrfs} && %{undefined _without_btrfs}
%define _with_btrfs 1
%endif

Name: docker-ce
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 3
Source0: engine.tgz
Summary: The open-source application container engine
Group: Tools/Docker
License: ASL 2.0
URL: https://www.docker.com
Vendor: Docker
Packager: Docker <support@docker.com>

Requires: /usr/sbin/groupadd
Requires: docker-ce-cli
Requires: docker-ce-rootless-extras
Requires: container-selinux >= 2:2.74
Requires: libseccomp >= 2.3
Requires: systemd
Requires: iptables
%if %{undefined rhel} || 0%{?rhel} < 9
# Libcgroup is no longer available in RHEL/CentOS >= 9 distros.
Requires: libcgroup
%endif
Requires: containerd.io >= 1.6.4
Requires: tar
Requires: xz

BuildRequires: bash
%{?_with_btrfs:BuildRequires: btrfs-progs-devel}
BuildRequires: ca-certificates
BuildRequires: cmake
BuildRequires: device-mapper-devel
BuildRequires: gcc
BuildRequires: git
BuildRequires: glibc-static
BuildRequires: libarchive
BuildRequires: libseccomp-devel
BuildRequires: libselinux-devel
BuildRequires: libtool
BuildRequires: libtool-ltdl-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: pkgconfig(systemd)
BuildRequires: selinux-policy-devel
BuildRequires: systemd-devel
BuildRequires: tar
BuildRequires: which
%if 0%{?fedora} > 35 || 0%{?rhel} != 7
BuildRequires: golang
%endif

# conflicting packages
Conflicts: docker
Conflicts: docker-io
Conflicts: docker-engine-cs
Conflicts: docker-ee

# Obsolete packages
Obsoletes: docker-ce-selinux
Obsoletes: docker-engine-selinux
Obsoletes: docker-engine

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
go env -w GO111MODULE=off
export PREFIX=${RPM_BUILD_DIR}
export AUTO_GOPATH=1

mkdir -p ${RPM_BUILD_DIR}/go/src/github.com/docker
ln -snf ${RPM_BUILD_DIR}/src/engine ${RPM_BUILD_DIR}/go/src/github.com/docker/docker

pushd ${RPM_BUILD_DIR}/src/engine
TMP_GOPATH="${RPM_BUILD_DIR}/go" hack/dockerfile/install/install.sh tini
VERSION=%{_origversion} PRODUCT=docker hack/make.sh dynbinary
popd

%check
ver="$(${RPM_BUILD_DIR}/bundles/dynbinary-daemon/dockerd --version)"; \
    test "$ver" = "Docker version %{_origversion}, build %{_gitcommit_engine}" && echo "PASS: daemon version OK" || (echo "FAIL: daemon version ($ver) did not match" && exit 1)

%install
install -D -p -m 0755 $(readlink -f ${RPM_BUILD_DIR}/bundles/dynbinary-daemon/dockerd) ${RPM_BUILD_ROOT}%{_bindir}/dockerd
install -D -p -m 0755 $(readlink -f ${RPM_BUILD_DIR}/bundles/dynbinary-daemon/docker-proxy) ${RPM_BUILD_ROOT}%{_bindir}/docker-proxy
install -D -p -m 0755 ${RPM_BUILD_DIR}/docker-init ${RPM_BUILD_ROOT}%{_bindir}/docker-init

# install systemd scripts
install -D -m 0644 ${RPM_BUILD_DIR}/src/engine/contrib/init/systemd/docker.service ${RPM_BUILD_ROOT}%{_unitdir}/docker.service
install -D -m 0644 ${RPM_BUILD_DIR}/src/engine/contrib/init/systemd/docker.socket ${RPM_BUILD_ROOT}%{_unitdir}/docker.socket

%files
%{_bindir}/dockerd
%{_bindir}/docker-proxy
%{_bindir}/docker-init
%{_unitdir}/docker.service
%{_unitdir}/docker.socket

%post
%systemd_post docker.service
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi

%preun
%systemd_preun docker.service

%postun
%systemd_postun_with_restart docker.service

%changelog
