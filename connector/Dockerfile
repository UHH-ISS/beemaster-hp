FROM debian:stretch
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    librocksdb-dev \
    python \
    python-dev \
    python-pip \
    swig \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Get actor framwork
WORKDIR /scratch
RUN curl -LO https://github.com/actor-framework/actor-framework/archive/0.14.5.tar.gz
RUN tar xzf 0.14.5.tar.gz
WORKDIR actor-framework-0.14.5
RUN ./configure
RUN make -j4 install

# Get broker repository
WORKDIR /scratch
RUN git clone --recursive https://github.com/bro/broker /scratch/broker-git
WORKDIR broker-git

# Use correct branches / submodules
RUN git checkout topic/mfischer/broker-multihop
RUN git submodule update
RUN ./configure
RUN make -j4 install

COPY src /opt/connector
COPY requirements.txt /opt/connector/.

WORKDIR /opt/connector

# Remove sources
RUN rm -rf /scratch

RUN pip install --upgrade pip setuptools wheel 
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["/usr/bin/python","connector.py"]
