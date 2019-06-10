FROM continuumio/anaconda:latest

#We'll need a conda environment, in py3
COPY python3_environment.yml python3_environment.yml
RUN conda env create -f python3_environment.yml
#RUN conda create -n python2 python=2.7

#RUN apt-get update && \
#    apt-get install \
#    apt-transport-https \
#    ca-certificates \
#    curl \
#    gnupg2 \
#    software-properties-common -y && \
#	curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
	
#RUN add-apt-repository \
#   "deb [arch=amd64] https://download.docker.com/linux/debian \
#   $(lsb_release -cs) \
#   stable"

#RUN apt-get update && \
#    apt-get install docker-ce docker-ce-cli containerd.io -y

RUN mkdir /kaikonnect/
WORKDIR /kaikonnect/
COPY convert_mzml.py convert_mzml.py



#RUN conda run python3 pip install pyteomics -y
#RUN source activate python3 && \
#	pip install pyteomics -y
