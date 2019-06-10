##### This script is responsible for some basic staging of necessary files for
##### both Kaiko (and its default network) and TagGraph.
sudo docker pull chambm/pwiz-skyline-i-agree-to-the-vendor-licenses && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
git clone https://github.com/PNNL-Comp-Mass-Spec/Kaiko.git && \
cd Kaiko && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
cd model && \
sh get_data.sh

