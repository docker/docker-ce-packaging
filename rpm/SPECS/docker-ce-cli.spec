%global debug_package %{nil}

Name: docker-ce-cli
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 1
Summary: The open-source application container engine
Group: Tools/Docker
License: ASL 2.0
Source0: cli.tgz
URL: https://www.docker.com
Vendor: Docker
Packager: Docker <support@docker.com>

# required packages on install
Requires: /bin/sh
Requires: /usr/sbin/groupadd

# CentOS 7 and RHEL 7 do not yet support weak dependencies
#
# Note that we're not using <= 7 here, to account for other RPM distros, such
# as Fedora, which would not have the rhel macro set (so default to 0).
%if 0%{?rhel} == 7
Requires: docker-buildx-plugin
Requires: docker-compose-plugin
%else
Recommends: docker-buildx-plugin
Recommends: docker-compose-plugin
%endif

# TODO change once we support scan-plugin on other architectures
%ifarch x86_64
# CentOS 7 and RHEL 7 do not yet support weak dependencies
#
# Note that we're not using <= 7 here, to account for other RPM distros, such
# as Fedora, which would not have the rhel macro set (so default to 0).
%if 0%{?rhel} == 7
Requires: docker-scan-plugin(x86-64)
%else
Recommends: docker-scan-plugin(x86-64)
%endif
%endif

BuildRequires: make
BuildRequires: libtool-ltdl-devel
BuildRequires: git
%if 0%{?fedora} < 36 || 0%{?rhel} == 7
BuildRequires: golang
%endif

# conflicting packages
Conflicts: docker
Conflicts: docker-io
Conflicts: docker-engine-cs
Conflicts: docker-ee
Conflicts: docker-ee-cli

%description
Docker is is a product for you to build, ship and run any application as a
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
go env -w GO111MODULE=off
export PREFIX=${RPM_BUILD_DIR}
export TMP_GOPATH="${RPM_BUILD_DIR}/go"
export GOPATH="${RPM_BUILD_DIR}/go"

mkdir -p ${RPM_BUILD_DIR}/go/src/github.com/docker
rm -f ${RPM_BUILD_DIR}/go/src/github.com/docker/cli
ln -snf ${RPM_BUILD_DIR}/src/cli ${RPM_BUILD_DIR}/go/src/github.com/docker/cli
pushd ${RPM_BUILD_DIR}/go/src/github.com/docker/cli
VERSION=%{_origversion} GITCOMMIT=%{_gitcommit_cli} GO_LINKMODE=dynamic ./scripts/build/binary && DISABLE_WARN_OUTSIDE_CONTAINER=1 make manpages # cli
popd

%check
ver="$(cli/build/docker --version)"; \
    test "$ver" = "Docker version %{_origversion}, build %{_gitcommit_cli}" && echo "PASS: cli version OK" || (echo "FAIL: cli version ($ver) did not match" && exit 1)

%install
# install binary
install -d ${RPM_BUILD_ROOT}%{_bindir}
install -p -m 755 cli/build/docker ${RPM_BUILD_ROOT}%{_bindir}/docker

# add bash, zsh, and fish completions
install -d ${RPM_BUILD_ROOT}%{_datadir}/bash-completion/completions
install -d ${RPM_BUILD_ROOT}%{_datadir}/zsh/vendor-completions
install -d ${RPM_BUILD_ROOT}%{_datadir}/fish/vendor_completions.d
install -p -m 644 cli/contrib/completion/bash/docker ${RPM_BUILD_ROOT}%{_datadir}/bash-completion/completions/docker
install -p -m 644 cli/contrib/completion/zsh/_docker ${RPM_BUILD_ROOT}%{_datadir}/zsh/vendor-completions/_docker
install -p -m 644 cli/contrib/completion/fish/docker.fish ${RPM_BUILD_ROOT}%{_datadir}/fish/vendor_completions.d/docker.fish

# install manpages
install -d ${RPM_BUILD_ROOT}%{_mandir}/man1
install -p -m 644 cli/man/man1/*.1 ${RPM_BUILD_ROOT}%{_mandir}/man1
install -d ${RPM_BUILD_ROOT}%{_mandir}/man5
install -p -m 644 cli/man/man5/*.5 ${RPM_BUILD_ROOT}%{_mandir}/man5
install -d ${RPM_BUILD_ROOT}%{_mandir}/man8
install -p -m 644 cli/man/man8/*.8 ${RPM_BUILD_ROOT}%{_mandir}/man8

mkdir -p build-docs
for cli_file in LICENSE MAINTAINERS NOTICE README.md; do
    cp "cli/$cli_file" "build-docs/$cli_file"
done

# list files owned by the package here
%files
%doc build-docs/LICENSE build-docs/MAINTAINERS build-docs/NOTICE build-docs/README.md
%{_bindir}/docker
%{_datadir}/bash-completion/completions/docker
%{_datadir}/zsh/vendor-completions/_docker
%{_datadir}/fish/vendor_completions.d/docker.fish
%doc
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*


%post
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi

%changelog
