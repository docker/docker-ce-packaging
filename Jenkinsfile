#!groovy

test_steps = [
	'deb': { ->
		stage('Ubuntu Xenial Debian Package') {
			wrappedNode(label: 'docker-edge && x86_64', cleanWorkspace: true) {
				checkout scm
				sh('git clone https://github.com/docker/cli.git')
				sh('git clone https://github.com/moby/moby.git')
				sh('make VERSION=0.0.1-dev DOCKER_BUILD_PKGS=ubuntu-xenial ENGINE_DIR=$(pwd)/moby CLI_DIR=$(pwd)/cli deb')
			}
		}
	},
	'rpm': { ->
		stage('Centos 7 RPM Package') {
			wrappedNode(label: 'docker-edge && x86_64', cleanWorkspace: true) {
				checkout scm
				sh('git clone https://github.com/docker/cli.git')
				sh('git clone https://github.com/moby/moby.git')
				sh('make VERSION=0.0.1-dev DOCKER_BUILD_PKGS=centos-7 ENGINE_DIR=$(pwd)/moby CLI_DIR=$(pwd)/cli rpm')
			}
		}
	},
	'static': { ->
		stage('Static Linux Binaries') {
			wrappedNode(label: 'docker-edge && x86_64', cleanWorkspace: true) {
				checkout scm
				sh('git clone https://github.com/docker/cli.git')
				sh('git clone https://github.com/moby/moby.git')
				sh('make VERSION=0.0.1-dev DOCKER_BUILD_PKGS=static-linux ENGINE_DIR=$(pwd)/moby CLI_DIR=$(pwd)/cli static')
			}
		}
	},
]

parallel(test_steps)
