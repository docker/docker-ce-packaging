#!groovy
pipeline {
	agent none
	options {
		buildDiscarder(logRotator(daysToKeepStr: '30'))
		timeout(time: 30, unit: 'MINUTES')
		timestamps()
	}
	parameters {
		string(name: 'github_repo_engine', defaultValue: 'docker/engine', description: 'github org/repo of engine')
		string(name: 'github_branch_engine', defaultValue: env.CHANGE_TARGET ?: env.BRANCH_NAME, description: 'github branch of engine')
		string(name: 'github_repo_cli', defaultValue: 'docker/cli', description: 'github org/repo of cli')
		string(name: 'github_branch_cli', defaultValue: env.CHANGE_TARGET ?: env.BRANCH_NAME, description: 'github branch of cli')
		booleanParam(name: 'archive_packages', defaultValue: false, description: 'archive packages')
	}
	environment {
		DOCKER_BUILDKIT = '1'
	}
	stages {
		stage('Build') {
			parallel {
				stage('ubuntu-xenial') {
					agent { label 'amd64 && ubuntu-1804 && overlay2' }
					stages {
						stage('create package') {
							steps {
								sh 'docker version'
								sh 'docker info'
								sh "git clone -b '$params.github_branch_engine' --depth 1 'https://github.com/$params.github_repo_engine' engine"
								sh "git clone -b '$params.github_branch_cli' --depth 1 'https://github.com/$params.github_repo_cli' cli"
								sh 'make -C deb VERSION=0.0.1-dev ENGINE_DIR=$(pwd)/engine CLI_DIR=$(pwd)/cli ubuntu-xenial'
							}
						}
						stage('archive package') {
							when { expression { params.archive_packages } }
							steps {
								archiveArtifacts artifacts: 'deb/debbuild/ubuntu-xenial/docker-ce*.deb'
							}
						}
					}
					post {
						cleanup {
							sh 'docker run --rm -v "$WORKSPACE:/workspace" busybox chown -R "$(id -u):$(id -g)" /workspace'
							deleteDir()
						}
					}
				}
				stage('centos-7') {
					agent { label 'amd64 && ubuntu-1804 && overlay2' }
					stages {
						stage('create package') {
							steps {
								sh 'docker version'
								sh 'docker info'
								sh "git clone -b '$params.github_branch_engine' --depth 1 'https://github.com/$params.github_repo_engine' engine"
								sh "git clone -b '$params.github_branch_cli' --depth 1 'https://github.com/$params.github_repo_cli' cli"
								sh 'make -C rpm VERSION=0.0.1-dev ENGINE_DIR=$(pwd)/engine CLI_DIR=$(pwd)/cli centos-7'
							}
						}
						stage('archive package') {
							when { expression { params.archive_packages } }
							steps {
								archiveArtifacts artifacts: 'rpm/rpmbuild/RPMS/x86_64/docker-ce*.rpm'
							}
						}
					}
					post {
						cleanup {
							sh 'docker run --rm -v "$WORKSPACE:/workspace" busybox chown -R "$(id -u):$(id -g)" /workspace'
							deleteDir()
						}
					}
				}
				stage('static') {
					agent { label 'amd64 && ubuntu-1804 && overlay2' }
					stages {
						stage('create package') {
							steps {
								sh 'docker version'
								sh 'docker info'
								sh "git clone -b '$params.github_branch_engine' --depth 1 'https://github.com/$params.github_repo_engine' engine"
								sh "git clone -b '$params.github_branch_cli' --depth 1 'https://github.com/$params.github_repo_cli' cli"
								sh 'make VERSION=0.0.1-dev DOCKER_BUILD_PKGS=static-linux ENGINE_DIR=$(pwd)/engine CLI_DIR=$(pwd)/cli static'
							}
						}
						stage('archive package') {
							when { expression { params.archive_packages } }
							steps {
								archiveArtifacts artifacts: 'static/build/linux/docker-*.tgz'
							}
						}
					}
					post {
						cleanup {
							sh 'docker run --rm -v "$WORKSPACE:/workspace" busybox chown -R "$(id -u):$(id -g)" /workspace'
							deleteDir()
						}
					}
				}
				stage('image') {
					agent { label 'amd64 && ubuntu-1804 && overlay2' }
					stages {
						stage('create image') {
							steps {
								sh 'docker version'
								sh 'docker info'
								sh "git clone -b '$params.github_branch_engine' --depth 1 'https://github.com/$params.github_repo_engine' engine"
								sh "git clone -b '$params.github_branch_cli' --depth 1 'https://github.com/$params.github_repo_cli' cli"
								sh 'make ENGINE_DIR=$(pwd)/engine image clean-image clean-engine'
							}
						}
					}
					post {
						cleanup {
							sh 'docker run --rm -v "$WORKSPACE:/workspace" busybox chown -R "$(id -u):$(id -g)" /workspace'
							deleteDir()
						}
					}
				}
			}
		}
	}
}
