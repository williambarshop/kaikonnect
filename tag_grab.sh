##### This script is responsible for some basic staging of necessary files for
##### both Kaiko (and its default network) and TagGraph.
git clone https://github.com/PNNL-Comp-Mass-Spec/Kaiko.git && \
cd Kaiko && \
chmod +x ${PWD}/build_docker.sh && \
${PWD}/build_docker.sh && \
cd model && \
sh get_data.sh

