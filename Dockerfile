FROM ubuntu:14.04

RUN apt-get -y update && apt-get install -y \
	libatlas-dev \
	python \
	python-flask \
	python-pip \
	python-dev \
	python-numpy \
	python-scipy
RUN rm -rf /var/lib/apt/lists/*
RUN pip install smart-open
COPY gensim.tar.gz .
RUN tar -xf gensim.tar.gz
RUN cd gensim-0.13.0rc1/ && python setup.py install && cd ../
COPY models models
RUN ls -la
COPY app.py .
EXPOSE 8001
ENTRYPOINT python app.py
