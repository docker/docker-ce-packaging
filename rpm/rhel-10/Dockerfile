# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:latest
ARG DISTRO=rhel
ARG SUITE=10
ARG BUILD_IMAGE=registry.access.redhat.com/ubi10/ubi

FROM ${GO_IMAGE} AS golang

FROM ${BUILD_IMAGE} AS subscribed-image
RUN --mount=type=secret,id=rh-user --mount=type=secret,id=rh-pass <<-EOT
	rm -f /etc/rhsm-host

	if [ ! -f /run/secrets/rh-user ] || [ ! -f /run/secrets/rh-pass ]; then
		echo "Either RH_USER or RH_PASS is not set. Running build without subscription."
	else
		subscription-manager register \
			--username="$(cat /run/secrets/rh-user)" \
			--password="$(cat /run/secrets/rh-pass)"

		subscription-manager repos --enable codeready-builder-for-rhel-10-$(arch)-rpms
		# dnf config-manager --set-enabled codeready-builder-for-rhel-10-$(arch)-rpms
	fi
EOT

FROM subscribed-image

ENV GOPROXY=https://proxy.golang.org|direct
ENV GO111MODULE=on
ENV GOPATH=/go
ENV GOTOOLCHAIN=local
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin
ENV AUTO_GOPATH=1
ENV DOCKER_BUILDTAGS="exclude_graphdriver_btrfs no_libnftables"
ARG DISTRO
ARG SUITE
ENV DISTRO=${DISTRO}
ENV SUITE=${SUITE}

RUN dnf install -y rpm-build
COPY --link SPECS /root/rpmbuild/SPECS
RUN dnf builddep --define '_no_libnftables true' -y /root/rpmbuild/SPECS/*.spec
COPY --link --from=golang /usr/local/go /usr/local/go
WORKDIR /root/rpmbuild
ENTRYPOINT ["/bin/rpmbuild"]
