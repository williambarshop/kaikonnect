##### This script is responsible for some basic staging of necessary files for
##### both Kaiko (and its default network) and TagGraph.

sudo docker pull chambm/pwiz-skyline-i-agree-to-the-vendor-licenses && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
wget https://sourceforge.net/projects/taggraph/files/Current%20Release/DockerContainer/linux/CentosDockerTG.1.7.1.tar.gz/download -O tg_docker.tar.gz && \
tar xzvf tg_docker.tar.gz && \
rm tg_docker.tar.gz && \
mkdir example && \
mv CentosDockerTG.1.7.1/sampleInputFiles.tar.gz example/tg_examples.tar.gz && \
cd example/ && \
mkdir mzml_files && \
tar xzvf tg_examples.tar.gz && \
rm tg_examples.tar.gz && \
mv samples/sampleInputFiles/mzML/ mzml_files/
mv samples/sampleInputFiles/FMIndices/human_uniprot_12092014_crap.fasta . && \
rm -rf samples/ && \
cd ../ && \
cd CentosDockerTG.1.7.1 && \
chmod +x ${PWD}/build.sh && \
sudo ./build.sh && \
cd .. && \
git clone https://github.com/PNNL-Comp-Mass-Spec/Kaiko.git && \
cd Kaiko && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
cd model && \
sh get_data.sh

