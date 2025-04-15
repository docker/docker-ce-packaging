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
# Provides modprobe, which we use to load br_netfilter if not loaded.
Suggests: kmod
Requires: docker-ce-cli
Recommends: docker-ce-rootless-extras
Requires: container-selinux
Requires: systemd
Requires: iptables
%if %{undefined rhel} || 0%{?rhel} < 9
# Libcgroup is no longer available in RHEL/CentOS >= 9 distros.
Requires: libcgroup
%endif
Requires: containerd.io >= 1.6.24
Requires: tar
Requires: xz

BuildRequires: bash
BuildRequires: ca-certificates
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: git
BuildRequires: glibc-static
BuildRequires: libtool
BuildRequires: libtool-ltdl-devel
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
VERSION=%{_origversion} PRODUCT=docker hack/make.sh dynbinary
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

# install systemd sysusers config
mkdir -p ${RPM_BUILD_ROOT}%{_sysusersdir}
echo "g docker -" >> ${RPM_BUILD_ROOT}%{_sysusersdir}/docker.conf
chmod 0644 ${RPM_BUILD_ROOT}%{_sysusersdir}/docker.conf
# install -D -p -m 0644 engine/contrib/systemd-sysusers/docker.conf ${RPM_BUILD_ROOT}%{_sysusersdir}/docker.conf

# install systemd scripts
install -D -p -m 0644 engine/contrib/init/systemd/docker.service ${RPM_BUILD_ROOT}%{_unitdir}/docker.service
install -D -p -m 0644 engine/contrib/init/systemd/docker.socket ${RPM_BUILD_ROOT}%{_unitdir}/docker.socket

# install manpages
make -C ${RPM_BUILD_DIR}/src/engine/man DESTDIR=${RPM_BUILD_ROOT} prefix=%{_mandir} install

# create the config directory
mkdir -p ${RPM_BUILD_ROOT}/etc/docker

%files
%{_bindir}/dockerd
%{_bindir}/docker-proxy
%{_libexecdir}/docker/docker-init
%{_unitdir}/docker.service
%{_unitdir}/docker.socket
%{_sysusersdir}/docker.conf
%{_mandir}/man*/*
%dir /etc/docker

%post
%systemd_post docker.service

%preun
%systemd_preun docker.service docker.socket

%postun
%systemd_postun_with_restart docker.service

%changelog
