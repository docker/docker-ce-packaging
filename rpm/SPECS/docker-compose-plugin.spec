%global debug_package %{nil}

Name: docker-compose-plugin
Version: %{_compose_rpm_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: compose.tgz
Summary: Docker Compose (V2) plugin for the Docker CLI
Group: Tools/Docker
License: ASL 2.0
URL: https://github.com/docker/compose/
Vendor: Docker
Packager: Docker <support@docker.com>

# CentOS 7 and RHEL 7 do not yet support weak dependencies.
#
# Note that we're not using <= 7 here, to account for other RPM distros, such
# as Fedora, which would not have the rhel macro set (so default to 0).
%if 0%{?rhel} != 7
Enhances: docker-ce-cli
%endif

BuildRequires: bash
%if 0%{?fedora} < 36 || 0%{?rhel} == 7
BuildRequires: golang
%endif

%description
Docker Compose (V2) plugin for the Docker CLI.

This plugin provides the 'docker compose' subcommand.

The binary can also be run standalone as a direct replacement for
Docker Compose V1 ('docker-compose').

%prep
%setup -q -c -n src -a 0

%build
pushd ${RPM_BUILD_DIR}/src/compose
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
pushd ${RPM_BUILD_DIR}/src/compose
    install -D -p -m 0755 bin/docker-compose ${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-compose
popd

for f in LICENSE MAINTAINERS NOTICE README.md; do
    install -D -p -m 0644 "${RPM_BUILD_DIR}/src/compose/$f" "docker-compose-plugin-docs/$f"
done

%files
%doc docker-compose-plugin-docs/*
%license docker-compose-plugin-docs/LICENSE
%license docker-compose-plugin-docs/NOTICE
%{_libexecdir}/docker/cli-plugins/docker-compose

%post

%preun

%postun

%changelog
