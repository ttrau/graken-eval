# graken-eval

## Thesis

Install and run the instructions within the ts branch of [ttrau/graken](https://github.com/ttrau/graken/tree/ts) to create a .graph file.

```sh
git clone -b ts https://github.com/ttrau/graken.git
```

Then either place the .graph file in `ts/graken.graph` and run the script in `ts/script` or add the path to the argument line.

```sh
ts/script <ts/graken.graph>
```

## Install

Install `graken-eval` with `pip`.

```sh
sudo dnf install python3-dev python3-pip
sudo apt install python3-devel python3-pip

pip3 install .
```

Additional dependencies (graphviz necessary to print the .svg graphs).

```sh
sudo apt install graphviz libcairo2-dev pkg-config python3-dev
```

Install `graph-tool` from source with the install script `graph-tool.sh` or from a repository if available.

## Develop

```sh
pip3 install . && graken-eval -I -d foo.graph
```
