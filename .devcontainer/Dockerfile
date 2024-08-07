# Download base image ubuntu 22.04
FROM ubuntu:22.04

# LABEL about the custom image
LABEL maintainer="dancioc@nus.edu.sg"
LABEL version="0.1"
LABEL description="This is a custom Docker Image for pymeca"

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive
# display
ENV DISPLAY=host.docker.internal:0.0
# timezone
ENV TZ=Asia/Singapore

# Update Ubuntu Software repository
# https://stackoverflow.com/questions/39760663/docker-ubuntu-bin-sh-1-locale-gen-not-found
# https://askubuntu.com/questions/162391/how-do-i-fix-my-locale-issue/229512#229512
# add etherum ppa
# install python/pip/cmake/solc
RUN apt-get update && apt upgrade -y
RUN apt-get install -y locales && locale-gen "en_US.UTF-8" && dpkg-reconfigure locales 
RUN apt-get install -y software-properties-common && apt-get update
RUN add-apt-repository ppa:ethereum/ethereum && apt-get update
RUN apt-get install -y curl zip unzip git cmake
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y solc

# install python packages web3/py-solc-x cid jupyter and poetry
#RUN pip3 install web3[tester] && \
#    pip3 install py-solc-x && \
#    pip3 install py-multiformats-cid && \
#    pip3 install jupyterlab && \
#    pip3 install poetry && \
#    pip3 install pytest && \
#    pip3 install pytest-cov && \
#    pip3 install myst-nb && \
#    pip3 install sphinx-rtd-theme && \
#    pip3 install sphinx-autodoc-typehints && \
#    pip3 install sphinx-autoapi

# install npm -> nodejs -> npm
ARG NODEJS_VERSION=20.11.1
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
RUN export NVM_DIR="${HOME}/.nvm" && \. "$NVM_DIR/nvm.sh" && \
    nvm install ${NODEJS_VERSION} && \
    nvm use ${NODEJS_VERSION} && \
    nvm install-latest-npm

# install poetry
RUN pip3 install poetry
# install pymeca
RUN poetry config virtualenvs.create false

RUN apt-get install -y python-is-python3

# install IPFS
RUN apt-get install -y wget
RUN wget https://github.com/ipfs/kubo/releases/download/v0.27.0/kubo_v0.27.0_linux-amd64.tar.gz
RUN tar -xvzf kubo_v0.27.0_linux-amd64.tar.gz
WORKDIR /kubo
RUN bash install.sh
