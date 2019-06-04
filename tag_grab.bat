##### This script is responsible for some basic staging of necessary files for
##### both Kaiko (and its default network) and TagGraph.
git clone https://github.com/PNNL-Comp-Mass-Spec/Kaiko.git
cd Kaiko
build_docker.sh
cd model
get_data.sh

