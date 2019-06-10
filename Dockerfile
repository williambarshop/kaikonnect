FROM continuumio/anaconda:latest

#We'll need two conda environments, in py3 and py2 for the accessory scripts...
COPY python3_environment.yml python3_environment.yml
RUN conda env create -f python3_environment.yml

COPY python2_environment.yml python2_environment.yml
RUN conda env create -f python2_environment.yml

RUN mkdir /kaikonnect/
WORKDIR /kaikonnect/
COPY convert_mzml.py convert_mzml.py
COPY taggraph_interconnect.py taggraph_interconnect.py


#RUN conda run python3 pip install pyteomics -y
#RUN source activate python3 && \
#	pip install pyteomics -y
