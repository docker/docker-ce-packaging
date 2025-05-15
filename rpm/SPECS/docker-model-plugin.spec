%global debug_package %{nil}

Name: docker-model-plugin
Version: %{_model_rpm_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: model.tgz
Summary: Docker Model Runner plugin for the Docker CLI
Group: Tools/Docker
License: Apache-2.0
URL: https://docs.docker.com/model-runner/
Vendor: Docker
Packager: Docker <support@docker.com>

Enhances: docker-ce-cli

BuildRequires: bash

%description
Docker Model Runner plugin for the Docker CLI.

This plugin provides the 'docker model' subcommand.

%prep
%setup -q -c -n src -a 0

%build
GO111MODULE=on make -C ${RPM_BUILD_DIR}/src/model VERSION=%{_model_version} ce-release

%check
ver="$(${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-model docker-cli-plugin-metadata | awk '{ gsub(/[",:]/,"")}; $1 == "Version" { print $2 }')"; \
    test "$ver" = "%{_model_version}" && echo "PASS: docker-model version OK" || (echo "FAIL: docker-model version ($ver) did not match" && exit 1)

%install
install -D -p -m 0755 ${RPM_BUILD_DIR}/src/model/dist/docker-model ${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-model

for f in LICENSE; do
    install -D -p -m 0644 "${RPM_BUILD_DIR}/src/model/$f" "docker-model-plugin-docs/$f"
done

%files
%doc docker-model-plugin-docs/*
%license docker-model-plugin-docs/LICENSE
%{_libexecdir}/docker/cli-plugins/docker-model

%post

%preun

%postun

%changelog
