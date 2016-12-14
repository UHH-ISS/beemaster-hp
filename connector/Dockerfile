FROM debian:stretch
RUN apt-get update && \
    apt-get upgrade -y
RUN apt-get install -y \
    build-essential \
    git \
    bison \
    flex \
    gawk \
    cmake \
    swig \
    libssl1.0-dev \
    libgeoip-dev \
    python \
    python-dev \
    python-pip \
    python-setuptools \
    libcurl4-openssl-dev \
    wget \
    libncurses5-dev \
    ca-certificates \
    librocksdb-dev \
    libpcap-dev \
    zlib1g-dev \
    libtcmalloc-minimal4 \
    curl \
    google-perftools \
    debhelper \
    bc \
    --no-install-recommends

# get actor framwork
WORKDIR /scratch
RUN curl -LO https://github.com/actor-framework/actor-framework/archive/0.14.5.tar.gz
RUN tar xzf 0.14.5.tar.gz
WORKDIR /scratch/actor-framework-0.14.5
RUN ./configure
RUN make -j4 install

# get broker repository
WORKDIR /scratch
RUN git clone --recursive https://github.com/bro/broker /scratch/broker-git
WORKDIR /scratch/broker-git

# use correct branches / submodules
RUN git checkout topic/mfischer/broker-multihop
RUN git submodule update
RUN ./configure
RUN make -j4 install

COPY src /opt/connector
COPY requirements.txt /opt/connector/.

WORKDIR /opt/connector
RUN pip install --upgrade pip setuptools wheel 
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["/usr/bin/python","connector.py"]
