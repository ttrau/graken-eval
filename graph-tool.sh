#!/bin/sh

sudo dnf groupinstall "Development Tools" "Development Libraries"
sudo dnf install python3-devel boost-devel gmp-devel CGAL-devel cairomm-devel sparsehash-devel
git clone https://git.skewed.de/count0/graph-tool.git graph-tool
cd graph-tool
./autogen.sh
./configure
make
sudo make install

