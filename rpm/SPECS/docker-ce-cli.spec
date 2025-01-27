%global debug_package %{nil}

Name: docker-ce-cli
Version: %{_version}
Release: %{_release}%{?dist}
Epoch: 1
Summary: The open-source application container engine
Group: Tools/Docker
License: Apache-2.0
Source0: cli.tgz
URL: https://www.docker.com
Vendor: Docker
Packager: Docker <support@docker.com>

# required packages on install
Requires: /bin/sh
Requires: /usr/sbin/groupadd

Recommends: docker-buildx-plugin
Recommends: docker-compose-plugin

BuildRequires: make
BuildRequires: libtool-ltdl-devel
BuildRequires: git

# conflicting packages
Conflicts: docker
Conflicts: docker-io
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
mkdir -p /go/src/github.com/docker
rm -f /go/src/github.com/docker/cli
ln -snf ${RPM_BUILD_DIR}/src/cli /go/src/github.com/docker/cli
make -C /go/src/github.com/docker/cli DISABLE_WARN_OUTSIDE_CONTAINER=1 VERSION=%{_origversion} GITCOMMIT=%{_gitcommit_cli} dynbinary manpages shell-completion

%check
ver="$(cli/build/docker --version)"; \
    test "$ver" = "Docker version %{_origversion}, build %{_gitcommit_cli}" && echo "PASS: cli version OK" || (echo "FAIL: cli version ($ver) did not match" && exit 1)

%install
# install binary
install -D -p -m 755 cli/build/docker ${RPM_BUILD_ROOT}%{_bindir}/docker

# add bash, zsh, and fish completions
install -D -p -m 644 cli/build/completion/bash/docker ${RPM_BUILD_ROOT}%{_datadir}/bash-completion/completions/docker
install -D -p -m 644 cli/build/completion/zsh/_docker ${RPM_BUILD_ROOT}%{_datadir}/zsh/vendor-completions/_docker
install -D -p -m 644 cli/build/completion/fish/docker.fish ${RPM_BUILD_ROOT}%{_datadir}/fish/vendor_completions.d/docker.fish

# install man-pages
for sec in $(seq 1 9); do
    if [ -d "cli/man/man${sec}" ]; then
        # Note: we need to create destination dirs first (instead "install -D") due to wildcards used.
        install -d ${RPM_BUILD_ROOT}%{_mandir}/man${sec} && \
        install -p -m 644 cli/man/man${sec}/*.${sec} ${RPM_BUILD_ROOT}%{_mandir}/man${sec};
    fi
done

mkdir -p build-docs
for cli_file in LICENSE MAINTAINERS NOTICE README.md; do
    install -D -p -m 644 "cli/$cli_file" "build-docs/$cli_file"
done

# list files owned by the package here
%files
%doc build-docs/LICENSE build-docs/MAINTAINERS build-docs/NOTICE build-docs/README.md
%{_bindir}/docker
%{_datadir}/bash-completion/completions/docker
%{_datadir}/zsh/vendor-completions/_docker
%{_datadir}/fish/vendor_completions.d/docker.fish
%{_mandir}/man*/*


%post
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi

%changelog
