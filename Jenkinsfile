#!groovy

def pkgs = [
    [target: "centos-7",                 image: "centos:7",                               arches: ["amd64", "aarch64"]],          // (EOL: June 30, 2024)
    [target: "centos-8",                 image: "quay.io/centos/centos:stream8",          arches: ["amd64", "aarch64"]],
    [target: "centos-9",                 image: "quay.io/centos/centos:stream9",          arches: ["amd64", "aarch64"]],
    [target: "debian-buster",            image: "debian:buster",                          arches: ["amd64", "aarch64", "armhf"]], // Debian 10 (EOL: 2024)
    [target: "debian-bullseye",          image: "debian:bullseye",                        arches: ["amd64", "aarch64", "armhf"]], // Debian 11 (Next stable)
    [target: "fedora-34",                image: "fedora:34",                              arches: ["amd64", "aarch64"]],          // EOL: May 17, 2022
    [target: "fedora-35",                image: "fedora:35",                              arches: ["amd64", "aarch64"]],          // EOL: November 30, 2022
    [target: "fedora-36",                image: "fedora:36",                              arches: ["amd64", "aarch64"]],          // EOL: May 24, 2023
    [target: "raspbian-buster",          image: "balenalib/rpi-raspbian:buster",          arches: ["armhf"]],                     // Debian/Raspbian 10 (EOL: 2024)
    [target: "raspbian-bullseye",        image: "balenalib/rpi-raspbian:bullseye",        arches: ["armhf"]],                     // Debian/Raspbian 11 (Next stable)
    [target: "ubuntu-bionic",            image: "ubuntu:bionic",                          arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 18.04 LTS (End of support: April, 2023. EOL: April, 2028)
    [target: "ubuntu-focal",             image: "ubuntu:focal",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 20.04 LTS (End of support: April, 2025. EOL: April, 2030)
    [target: "ubuntu-impish",            image: "ubuntu:impish",                          arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 21.10 (EOL: July, 2022)
    [target: "ubuntu-jammy",             image: "ubuntu:jammy",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 22.04 LTS (End of support: April, 2027. EOL: April, 2032)
]

def statics = [
    [os: "linux",       arches: ["amd64", "armv6", "armv7", "aarch64"]],
    [os: "darwin",      arches: ["amd64", "aarch64"]],
    [os: "windows",     arches: ["amd64"]],
]

def genPkgStep(LinkedHashMap pkg, String arch) {
    def nodeLabel = "linux&&${arch}"
    def branch = env.CHANGE_TARGET ?: env.BRANCH_NAME
    if (arch == 'armhf') {
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
                sh 'env|sort'
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

def genPkgSteps(opts) {
    return opts.arches.collectEntries {
        ["${opts.image}-${it}": genPkgStep(opts, it)]
    }
}

def genStaticStep(LinkedHashMap pkg, String arch) {
    def config = [
        amd64:   [label: "x86_64",      targetarch: "amd64"],
        aarch64: [label: "aarch64",     targetarch: "arm64"],
        armv6:   [label: "aarch64",     targetarch: "arm/v6"],
        armv7:   [label: "aarch64",     targetarch: "arm/v7"],
        ppc64le: [label: "ppc64le",     targetarch: "ppc64le"],
        s390x  : [label: "s390x",       targetarch: "s390x"],
    ][arch]
    def nodeLabel = "linux&&${config.label}"
    if (config.label == 'x86_64') {
        nodeLabel = "${nodeLabel}&&ubuntu"
    }
    def branch = env.CHANGE_TARGET ?: env.BRANCH_NAME
    return { ->
        wrappedNode(label: nodeLabel, cleanWorkspace: true) {
            stage("static-${pkg.os}-${arch}") {
                // This is just a "dummy" stage to make the distro/arch visible
                // in Jenkins' BlueOcean view, which truncates names....
                sh 'echo starting...'
            }
            stage("info") {
                sh 'docker version'
                sh 'docker info'
                sh 'env|sort'
            }
            stage("build") {
                try {
                    checkout scm
                    sh "make REF=$branch TARGETPLATFORM=${pkg.os}/${config.targetarch} static"
                } finally {
                    sh "make clean"
                }
            }
        }
    }
}

def genStaticSteps(opts) {
    return opts.arches.collectEntries {
        ["static-${opts.os}-${it}": genStaticStep(opts, it)]
    }
}

def parallelStages = pkgs.collectEntries { genPkgSteps(it) }
parallelStages << statics.collectEntries { genStaticSteps(it) }

parallel(parallelStages)
