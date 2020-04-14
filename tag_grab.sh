##### This script is responsible for some basic staging of necessary files for
##### both Kaiko (and its default network) and TagGraph.

sudo docker pull chambm/pwiz-skyline-i-agree-to-the-vendor-licenses && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
wget https://sourceforge.net/projects/taggraph/files/CurrentRelease-TagGraph.1.8/DockerContainer/Centos7/CentosDockerTG.1.8.1.tar.gz/download -O tg_docker.tar.gz && \
tar xzvf tg_docker.tar.gz && \
rm tg_docker.tar.gz && \
mkdir example && \
mv CentosDockerTG.1.8.1/sampleInputFiles.1.8.docker.tar.gz example/tg_examples.tar.gz && \
cd example/ && \
mkdir mzml_files && \
tar xzvf tg_examples.tar.gz && \
rm tg_examples.tar.gz && \
mv sampleInputFiles.1.8.docker/mzML/* mzml_files/
mv sampleInputFiles.1.8.docker/FMIndices/human_uniprot_12092014_crap.fasta . && \
rm -rf sampleInputFiles.1.8.docker/ && \
cd ../ && \
cd CentosDockerTG.1.8.1 && \
sed -i 's/pip install/pip install --upgrade pip \&\& pip install/' Dockerfile && \
chmod +x ${PWD}/build.sh && \
sudo ./build.sh && \
cd .. && \
git clone https://github.com/PNNL-Comp-Mass-Spec/Kaiko.git && \
cd Kaiko && \
chmod +x ${PWD}/build_docker.sh && \
sudo ${PWD}/build_docker.sh && \
cd model && \
sh get_data.sh

