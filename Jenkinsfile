#!groovy

def branch = env.CHANGE_TARGET ?: env.BRANCH_NAME

def pkgs = [
    [target: "centos-9",                 image: "quay.io/centos/centos:stream9",          arches: ["amd64", "aarch64"]],
    [target: "centos-10",                image: "quay.io/centos/centos:stream10",         arches: ["amd64", "aarch64"]],          // CentOS Stream 10 (EOL: 2030)
    [target: "debian-bullseye",          image: "debian:bullseye",                        arches: ["amd64", "aarch64", "armhf"]], // Debian 11 (oldstable, EOL: 2024-08-14, EOL (LTS): 2026-08-31)
    [target: "debian-bookworm",          image: "debian:bookworm",                        arches: ["amd64", "aarch64", "armhf"]], // Debian 12 (stable, EOL: 2026-06-10, EOL (LTS): 2028-06-30)
    [target: "fedora-40",                image: "fedora:40",                              arches: ["amd64", "aarch64"]],          // EOL: May 13, 2025
    [target: "fedora-41",                image: "fedora:41",                              arches: ["amd64", "aarch64"]],          // EOL: November 19, 2025
    [target: "fedora-42",                image: "fedora:42",                              arches: ["amd64", "aarch64"]],          // EOL: May 13, 2026
    [target: "raspbian-bullseye",        image: "balenalib/rpi-raspbian:bullseye",        arches: ["armhf"]],                     // Debian/Raspbian 11 (stable)
    [target: "raspbian-bookworm",        image: "balenalib/rpi-raspbian:bookworm",        arches: ["armhf"]],                     // Debian/Raspbian 12 (next stable)
    [target: "ubuntu-focal",             image: "ubuntu:focal",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 20.04 LTS (End of support: April, 2025. EOL: April, 2030)
    [target: "ubuntu-jammy",             image: "ubuntu:jammy",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 22.04 LTS (End of support: June,  2027. EOL: April, 2032)
    [target: "ubuntu-noble",             image: "ubuntu:noble",                           arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 24.04 LTS (End of support: June,  2029. EOL: April, 2034)
    [target: "ubuntu-oracular",          image: "ubuntu:oracular",                        arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 24.10 (EOL: July, 2025)
    [target: "ubuntu-plucky",            image: "ubuntu:plucky",                          arches: ["amd64", "aarch64", "armhf"]], // Ubuntu 25.04 (EOL: January, 2026)
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
                sh "make REF=$branch ARCH=${arch} ${pkg.target}"
            }
            stage("verify") {
                sh "make IMAGE=${pkg.image} ARCH=${arch} verify"
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
