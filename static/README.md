# Building your own Docker static package

Static packages can be built from root directory with the following syntax

```console
make STATICOS=${STATICOS} STATICOS=${STATICARCH} static
```

Format of `STATICOS`, `STATICARCH` should respect the current folder structure on
[download.docker.com](https://download-stage.docker.com/linux/static/stable/) like
`STATICOS=linux STATICARCH=armhf`.

Artifacts will be located in `build` under `build/$STATICOS/$STATICARCH/`.

### Building from local source

Specify the location of the source repositories for the engine and cli when
building packages

* `ENGINE_DIR` -> Specifies the directory where the engine code is located, eg: `$GOPATH/src/github.com/docker/docker`
* `CLI_DIR` -> Specifies the directory where the cli code is located, eg: `$GOPATH/src/github.com/docker/cli`

```shell
make ENGINE_DIR=/path/to/engine CLI_DIR=/path/to/cli STATICOS=linux STATICARCH=x86_64 static
```

## Supported platforms

Here is a list of platforms that are currently supported:

```console
make STATICOS=linux STATICARCH=x86_64 static
make STATICOS=linux STATICARCH=armel static
make STATICOS=linux STATICARCH=armhf static
make STATICOS=linux STATICARCH=aarch64 static
make STATICOS=darwin STATICARCH=x86_64 static
make STATICOS=darwin STATICARCH=aarch64 static
make STATICOS=windows STATICARCH=x86_64 static
```

> note: `darwin` only packages the docker cli and plugins.

But you can test building against whatever platform you want like:

```console
make STATICOS=linux STATICARCH=riscv64 static
make STATICOS=linux STATICARCH=s390x static
```
