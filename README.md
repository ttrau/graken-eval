# graken-eval

## Install

Install `graken-eval` with `pip`.

```sh
sudo dnf install python3-dev python3-pip
sudo apt install python3-devel python3-pip

pip3 install .
```

Additional dependencies.

```sh
sudo apt install libcairo2-dev pkg-config python3-dev
```

Install `graph-tool` from source with the install script `graph-tool.sh` or from a repository if available.

## Develop

```sh
pip3 install . && graken-eval -I -d foo.graph
```
