%global debug_package %{nil}

Name: docker-compose-plugin
Version: %{_compose_rpm_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: compose-cli.tgz
Summary: Docker Compose plugin for the Docker CLI
Group: Tools/Docker
License: ASL 2.0
URL: https://github.com/docker/compose-cli/
Vendor: Docker
Packager: Docker <support@docker.com>

BuildRequires: bash

%description
Docker Compose plugin for the Docker CLI.

%prep
%setup -q -c -n src -a 0

%build
pushd ${RPM_BUILD_DIR}/src/compose-cli
# FIXME: using GOPROXY, to work around:
# go: github.com/Azure/azure-sdk-for-go@v48.2.0+incompatible: reading github.com/Azure/azure-sdk-for-go/go.mod at revision v48.2.0: unknown revision v48.2.0
GOPROXY="https://proxy.golang.org" GO111MODULE=on go mod download
GOPROXY="https://proxy.golang.org" GO111MODULE=on GIT_TAG="%{_compose_version}" \
    make COMPOSE_BINARY="bin/docker-compose" -f builder.Makefile compose-plugin
popd

%check
ver="$(${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-compose docker-cli-plugin-metadata | awk '{ gsub(/[",:]/,"")}; $1 == "Version" { print $2 }')"; \
	test "$ver" = "%{_compose_version}" && echo "PASS: docker-compose version OK" || (echo "FAIL: docker-compose version ($ver) did not match" && exit 1)

%install
pushd ${RPM_BUILD_DIR}/src/compose-cli
install -D -p -m 0755 bin/docker-compose ${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-compose
popd

%files
%{_libexecdir}/docker/cli-plugins/docker-compose

%post

%preun

%postun

%changelog
