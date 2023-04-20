#!groovy

def branch = env.CHANGE_TARGET ?: env.BRANCH_NAME

def pkgs = [
    [target: "centos-7",                 image: "centos:7",                               arches: ["amd64", "aarch64"]],          // (EOL: June 30, 2024)
    [target: "centos-8",                 image: "quay.io/centos/centos:stream8",          arches: ["amd64", "aarch64"]],
    [target: "centos-9",                 image: "quay.io/centos/centos:stream9",          arches: ["amd64", "aarch64"]],
    [target: "debian-buster",            image: "debian:buster",                          arches: ["amd64", "aarch64", "armhf"]], // Debian 10 (EOL: 2024)
    [target: "debian-bullseye",          image: "debian:bullseye",                        arches: ["amd64", "aarch64", "armhf"]], // Debian 11 (stable)
    [target: "debian-bookworm",          image: "debian:bookworm",                        arches: ["amd64", "aarch64", "armhf"]], // Debian 12 (Next stable)
    [target: "fedora-36",                image: "fedora:36",                              arches: ["amd64", "aarch64"]],          // EOL: May 16, 2023
    [target: "fedora-37",                image: "fedora:37",                              arches: ["amd64", "aarch64"]],          // EOL: November 14, 2023
    [target: "fedora-38",                image: "fedora:38",                              arches: ["amd64", "aarch64"]],          // EOL: May 14, 2024
    [target: "fedora-39",                image: "fedora:39",                              arches: ["amd64", "aarch64"]],          // EOL: November 12, 2024
    [target: "raspbian-buster",          image: "balenalib/rpi-raspbian:buster",          arches: ["armhf"]],                     // Debian/Raspbian 10 (EOL: 2024)
    [target: "raspbian-bullseye",        image: "balenalib/rpi-raspbian:bullseye",        arches: ["armhf"]],                     // Debian/Raspbian 11 (stable)
    [target: "raspbian-bookworm",        image: "balenalib/rpi-raspbian:bookworm",        arches: ["armhf"]],                     // Debian/Raspbian 12 (next stable)
    [target: "ubuntu-bionic",            image: "ubuntu:bionic",                          arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 18.04 LTS (End of support: April, 2023. EOL: April, 2028)
    [target: "ubuntu-focal",             image: "ubuntu:focal",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 20.04 LTS (End of support: April, 2025. EOL: April, 2030)
    [target: "ubuntu-jammy",             image: "ubuntu:jammy",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 22.04 LTS (End of support: April, 2027. EOL: April, 2032)
    [target: "ubuntu-kinetic",           image: "ubuntu:kinetic",                         arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 22.10 (EOL: July, 2023)
    [target: "ubuntu-lunar",             image: "ubuntu:lunar",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 23.04 (EOL: January, 2024)
]

def genBuildStep(LinkedHashMap pkg, String arch) {
    def nodeLabel = "linux&&${arch}"
    def platform = ""
    def branch = env.CHANGE_TARGET ?: env.BRANCH_NAME

    if (arch == 'armhf') {
        // Running armhf builds on EC2 requires --platform parameter
        // Otherwise it accidentally pulls armel images which then breaks the verify step
        platform = "--platform=linux/${arch}"
        nodeLabel = "${nodeLabel}&&ubuntu"
    } else {
        nodeLabel = "${nodeLabel}&&ubuntu-2004"
    }
    return { ->
        wrappedNode(label: nodeLabel, cleanWorkspace: true) {
            stage("${pkg.target}-${arch}") {
                // This is just a "dummy" stage to make the distro/arch visible
                // in Jenkins' BlueOcean view, which truncates names....
                sh 'echo starting...'
            }
            stage("info") {
                sh 'docker version'
                sh 'docker info'
            }
            stage("build") {
                checkout scm
                sh "make clean"
                sh "make REF=$branch ${pkg.target}"
            }
            stage("verify") {
                sh "make IMAGE=${pkg.image} verify"
            }
        }
    }
}

def build_package_steps = [
    'static-linux': { ->
        wrappedNode(label: 'ubuntu-2004 && x86_64', cleanWorkspace: true) {
            stage("static-linux") {
                // This is just a "dummy" stage to make the distro/arch visible
                // in Jenkins' BlueOcean view, which truncates names....
                sh 'echo starting...'
            }
            stage("info") {
                sh 'docker version'
                sh 'docker info'
            }
            stage("build") {
                try {
                    checkout scm
                    sh "make REF=$branch DOCKER_BUILD_PKGS='static-linux' static"
                } finally {
                    sh "make clean"
                }
            }
        }
    },
    'cross-mac': { ->
        wrappedNode(label: 'ubuntu-2004 && x86_64', cleanWorkspace: true) {
            stage("cross-mac") {
                // This is just a "dummy" stage to make the distro/arch visible
                // in Jenkins' BlueOcean view, which truncates names....
                sh 'echo starting...'
            }
            stage("info") {
                sh 'docker version'
                sh 'docker info'
            }
            stage("build") {
                try {
                    checkout scm
                    sh "make REF=$branch DOCKER_BUILD_PKGS='cross-mac' static"
                } finally {
                    sh "make clean"
                }
            }
        }
    },
    'cross-win': { ->
        wrappedNode(label: 'ubuntu-2004 && x86_64', cleanWorkspace: true) {
            stage("cross-win") {
                // This is just a "dummy" stage to make the distro/arch visible
                // in Jenkins' BlueOcean view, which truncates names....
                sh 'echo starting...'
            }
            stage("info") {
                sh 'docker version'
                sh 'docker info'
            }
            stage("build") {
                try {
                    checkout scm
                    sh "make REF=$branch DOCKER_BUILD_PKGS='cross-win' static"
                } finally {
                    sh "make clean"
                }
            }
        }
    },
]

def genPackageSteps(opts) {
    return opts.arches.collectEntries {
        ["${opts.image}-${it}": genBuildStep(opts, it)]
    }
}

build_package_steps << pkgs.collectEntries { genPackageSteps(it) }

parallel(build_package_steps)
