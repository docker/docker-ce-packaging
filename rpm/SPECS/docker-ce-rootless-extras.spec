%global debug_package %{nil}

Name: docker-ce-rootless-extras
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: engine.tgz
Summary: Rootless support for Docker
Group: Tools/Docker
License: Apache-2.0
URL: https://docs.docker.com/engine/security/rootless/
Vendor: Docker
Packager: Docker <support@docker.com>

Requires: docker-ce
# TODO: conditionally add `Requires: dbus-daemon` for Fedora and CentOS 8

BuildRequires: bash

# conflicting packages
Conflicts: rootlesskit

%description
Rootless support for Docker.
Use dockerd-rootless.sh to run the daemon.
Use dockerd-rootless-setuptool.sh to setup systemd for dockerd-rootless.sh .

%prep
%setup -q -c -n src -a 0

%build

export DOCKER_GITCOMMIT=%{_gitcommit_engine}
mkdir -p /go/src/github.com/docker
ln -snf ${RPM_BUILD_DIR}/src/engine /go/src/github.com/docker/docker
TMP_GOPATH="/go" ${RPM_BUILD_DIR}/src/engine/hack/dockerfile/install/install.sh rootlesskit dynamic

%check
/usr/local/bin/rootlesskit -v

%install
install -D -p -m 0755 engine/contrib/dockerd-rootless.sh ${RPM_BUILD_ROOT}%{_bindir}/dockerd-rootless.sh
install -D -p -m 0755 engine/contrib/dockerd-rootless-setuptool.sh ${RPM_BUILD_ROOT}%{_bindir}/dockerd-rootless-setuptool.sh
install -D -p -m 0755 /usr/local/bin/rootlesskit ${RPM_BUILD_ROOT}%{_bindir}/rootlesskit

%files
%{_bindir}/dockerd-rootless.sh
%{_bindir}/dockerd-rootless-setuptool.sh
%{_bindir}/rootlesskit

%post

%preun

%postun

%changelog
