variable "VERSION" {
  default = "0.0.1-dev"
}
variable "DEFAULT_PRODUCT_LICENSE" {
  default = "Community Engine"
}
variable "PACKAGER_NAME" {
  default = "Docker, Inc."
}
variable "PLATFORM" {
  default = "Docker Engine - Community"
}
variable "GO_VERSION" {
  default = "1.17.8"
}
variable "RELEASE_OUT" {
  default = "./build"
}

target "_common" {
  args = {
    VERSION = VERSION
    DEFAULT_PRODUCT_LICENSE = DEFAULT_PRODUCT_LICENSE
    PACKAGER_NAME = PACKAGER_NAME
    PLATFORM = PLATFORM
    GO_IMAGE = "golang"
    GO_VERSION = GO_VERSION
    GO_IMAGE_VARIANT = "bullseye"
  }
  target = "release"
  output = [RELEASE_OUT]
}

group "default" {
  targets = ["debian-bullseye"]
}

group "deb" {
  targets = [
    "debian-bullseye",
    "debian-buster",
    "raspbian-bullseye",
    "raspbian-buster",
    "ubuntu-bionic",
    "ubuntu-focal",
    "ubuntu-hirsute",
    "ubuntu-impish",
    "ubuntu-jammy"
  ]
}

target "_deb_common" {
  inherits = ["_common"]
  args = {
    PKG_TYPE = "deb"
    EPOCH = 5
  }
}

target "debian-bullseye" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="debian"
    PKG_SUITE="bullseye"
    BUILD_IMAGE="debian"
    BUILD_IMAGE_VERSION="bullseye"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "debian-buster" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="debian"
    PKG_SUITE="buster"
    BUILD_IMAGE="debian"
    BUILD_IMAGE_VERSION="buster"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "raspbian-bullseye" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="raspbian"
    PKG_SUITE="bullseye"
    BUILD_IMAGE="balenalib/rpi-raspbian"
    BUILD_IMAGE_VERSION="bullseye"
  }
  platforms = [
    "linux/arm"
  ]
}

target "raspbian-buster" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="raspbian"
    PKG_SUITE="buster"
    BUILD_IMAGE="balenalib/rpi-raspbian"
    BUILD_IMAGE_VERSION="buster"
  }
  platforms = [
    "linux/arm",
  ]
}

target "ubuntu-bionic" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="ubuntu"
    PKG_SUITE="bionic"
    BUILD_IMAGE="ubuntu"
    BUILD_IMAGE_VERSION="bionic"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "ubuntu-focal" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="ubuntu"
    PKG_SUITE="focal"
    BUILD_IMAGE="ubuntu"
    BUILD_IMAGE_VERSION="focal"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "ubuntu-hirsute" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="ubuntu"
    PKG_SUITE="hirsute"
    BUILD_IMAGE="ubuntu"
    BUILD_IMAGE_VERSION="hirsute"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "ubuntu-impish" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="ubuntu"
    PKG_SUITE="impish"
    BUILD_IMAGE="ubuntu"
    BUILD_IMAGE_VERSION="impish"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}

target "ubuntu-jammy" {
  inherits = ["_deb_common"]
  args = {
    PKG_DISTRO="ubuntu"
    PKG_SUITE="jammy"
    BUILD_IMAGE="ubuntu"
    BUILD_IMAGE_VERSION="jammy"
  }
  platforms = [
    "linux/amd64",
    "linux/arm",
    "linux/arm64"
  ]
}
