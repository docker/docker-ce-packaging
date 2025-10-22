%global debug_package %{nil}

Name: docker-compose-plugin
Version: %{_compose_rpm_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: compose.tgz
Summary: Docker Compose (V2) plugin for the Docker CLI
Group: Tools/Docker
License: Apache-2.0
URL: https://github.com/docker/compose/
Vendor: Docker
Packager: Docker <support@docker.com>

Enhances: docker-ce-cli
Recommends: docker-buildx-plugin >= 0.17.0

BuildRequires: bash

%description
Docker Compose (V2) plugin for the Docker CLI.

This plugin provides the 'docker compose' subcommand.

The binary can also be run standalone as a direct replacement for
Docker Compose V1 ('docker-compose').

%prep
%setup -q -c -n src -a 0

%build
make -C ${RPM_BUILD_DIR}/src/compose VERSION=%{_compose_version} DESTDIR=./bin build

%check
ver="$(${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-compose docker-cli-plugin-metadata | awk '{ gsub(/[",:]/,"")}; $1 == "Version" { print $2 }')"; \
    test "$ver" = "%{_compose_version}" && echo "PASS: docker-compose version OK" || (echo "FAIL: docker-compose version ($ver) did not match" && exit 1)

%install
install -D -p -m 0755 ${RPM_BUILD_DIR}/src/compose/bin/docker-compose ${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-compose

for f in LICENSE NOTICE README.md; do
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
