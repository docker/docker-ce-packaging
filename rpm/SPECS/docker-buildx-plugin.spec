%global debug_package %{nil}

Name: docker-buildx-plugin
Version: %{_buildx_rpm_version}
Release: %{_release}%{?dist}
Epoch: 0
Source0: buildx.tgz
Summary: Docker Buildx plugin for the Docker CLI
Group: Tools/Docker
License: Apache-2.0
URL: https://github.com/docker/buildx
Vendor: Docker
Packager: Docker <support@docker.com>

BuildRequires: bash

%description
Docker Buildx plugin for the Docker CLI.

%prep
%setup -q -c -n src -a 0

%build
pushd ${RPM_BUILD_DIR}/src/buildx
	GO111MODULE=on \
	CGO_ENABLED=0 \
		go build \
			-mod=vendor \
			-trimpath \
			-ldflags="-w -X github.com/docker/buildx/version.Version=%{_buildx_version} -X github.com/docker/buildx/version.Revision=%{_buildx_gitcommit} -X github.com/docker/buildx/version.Package=github.com/docker/buildx" \
			-o "bin/docker-buildx" \
			./cmd/buildx
popd

%check
ver="$(${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-buildx docker-cli-plugin-metadata | awk '{ gsub(/[",:]/,"")}; $1 == "Version" { print $2 }')"; \
	test "$ver" = "%{_buildx_version}" && echo "PASS: docker-buildx version OK" || (echo "FAIL: docker-buildx version ($ver) did not match" && exit 1)

%install
install -D -p -m 0755 ${RPM_BUILD_DIR}/src/buildx/bin/docker-buildx ${RPM_BUILD_ROOT}%{_libexecdir}/docker/cli-plugins/docker-buildx

%files
%{_libexecdir}/docker/cli-plugins/docker-buildx

%post

%preun

%postun

%changelog
