#!groovy

pipeline {
	agent {
		label 'linux&&x86_64'
	}

	stages {
		stage('Clone upstream sources') {
			steps {
				sh 'git clone https://github.com/docker/engine engine'
				sh 'git clone https://github.com/docker/cli cli'
			}
		}
		stage('Test') {
			parallel {
				stage('Ubuntu 18.04') {
					steps {
						sh 'make -C deb ENGINE_DIR=$(readlink -e engine/) CLI_DIR=$(readlink -e cli/) ubuntu-bionic'
					}
				}
				stage('CentOS 7') {
					steps {
						sh 'make -C rpm ENGINE_DIR=$(readlink -e engine/) CLI_DIR=$(readlink -e cli/) centos-7'
					}
				}
				stage('Static Linux') {
					steps {
						sh 'make -C static ENGINE_DIR=$(readlink -e engine/) CLI_DIR=$(readlink -e cli/) static-linux'
					}
				}
				stage('Cross Mac') {
					steps {
						sh 'make -C static ENGINE_DIR=$(readlink -e engine/) CLI_DIR=$(readlink -e cli/) cross-mac'
					}
				}
				stage('Cross Windows') {
					steps {
						sh 'make -C static ENGINE_DIR=$(readlink -e engine/) CLI_DIR=$(readlink -e cli/) cross-win'
					}
				}
			}
		}
	}

	post {
		cleanup {
			deleteDir() /* clean up our workspace */
		}
	}
}
