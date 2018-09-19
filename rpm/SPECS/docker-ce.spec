%global debug_package %{nil}

Name: docker-ce
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 3
Source0: engine.tgz
Source1: docker.service
Summary: The open-source application container engine
Group: Tools/Docker
License: ASL 2.0
URL: https://www.docker.com
Vendor: Docker
Packager: Docker <support@docker.com>

Requires: docker-ce-cli
Requires: container-selinux >= 2.9
Requires: systemd-units
Requires: iptables
# Should be required as well by docker-ce-cli but let's just be thorough
Requires: containerd.io

BuildRequires: bash
BuildRequires: btrfs-progs-devel
BuildRequires: ca-certificates
BuildRequires: cmake
BuildRequires: device-mapper-devel
BuildRequires: gcc
BuildRequires: git
BuildRequires: glibc-static
BuildRequires: libseccomp-devel
BuildRequires: libtool
BuildRequires: make
BuildRequires: pkgconfig(systemd)
BuildRequires: selinux-policy-devel
BuildRequires: systemd-devel
BuildRequires: which

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
Docker is an open source project to build, ship and run any application as a
lightweight container.

Docker containers are both hardware-agnostic and platform-agnostic. This means
they can run anywhere, from your laptop to the largest EC2 compute instance and
everything in between - and they don't require you to use a particular
language, framework or packaging system. That makes them great building blocks
for deploying and scaling web apps, databases, and backend services without
depending on a particular stack or provider.

%prep
%setup -q -c -n src

%build
pushd docker
for component in tini "proxy dynamic";do
    TMP_GOPATH="/go" hack/dockerfile/install/install.sh $component
done
hack/make.sh dynbinary
popd

%check
docker/bundles/dynbinary-daemon/dockerd -v

%install
install -D -m 0755 $(readlink -f docker/bundles/dynbinary-daemon/dockerd) $RPM_BUILD_ROOT/%{_bindir}/dockerd
install -D -m 0755 /usr/local/bin/docker-proxy $RPM_BUILD_ROOT/%{_bindir}/docker-proxy
install -D -m 0755 /usr/local/bin/docker-init $RPM_BUILD_ROOT/%{_bindir}/docker-init
install -D -m 0644 %{_topdir}/SOURCES/docker.service $RPM_BUILD_ROOT/%{_unitdir}/docker.service

%files
/%{_bindir}/dockerd
/%{_bindir}/docker-proxy
/%{_bindir}/docker-init
/%{_unitdir}/docker.service

%pre
if [ $1 -gt 0 ] ; then
    # package upgrade scenario, before new files are installed

    # clear any old state
    rm -f %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :

    # check if docker service is running
    if systemctl is-active docker > /dev/null 2>&1; then
        systemctl stop docker > /dev/null 2>&1 || :
        touch %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :
    fi
fi

%post
%systemd_post docker
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi

%preun
%systemd_preun docker

%postun
%systemd_postun_with_restart docker

%posttrans
if [ $1 -ge 0 ] ; then
    # package upgrade scenario, after new files are installed

    # check if docker was running before upgrade
    if [ -f %{_localstatedir}/lib/rpm-state/docker-is-active ]; then
        systemctl start docker > /dev/null 2>&1 || :
        rm -f %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :
    fi
fi

%changelog
