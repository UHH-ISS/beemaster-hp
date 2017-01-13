#FROM debian:stretch
# Use this for raspberry
FROM resin/rpi-raspbian:jessie

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    cmake \
#    curl \
#    git \
#    librocksdb-dev \
#    python \
#    python-dev \
#    python-pip \
#    swig \
#    --no-install-recommends && \
#    rm -rf /var/lib/apt/lists/*

# RPi does not need/have rocksdb
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    python \
    python-dev \
    python-pip \
    swig \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install gcc-6
RUN echo 'deb http://mirrordirector.raspbian.org/raspbian/ testing main contrib non-free rpi' > /etc/apt/sources.list.d/stretch.list
RUN apt-get update && apt-get install -y \
    gcc-6 g++-6 \
    --no-install-recommends

# Get actor framwork
WORKDIR /scratch
RUN curl -LO https://github.com/actor-framework/actor-framework/archive/0.14.5.tar.gz
RUN tar xzf 0.14.5.tar.gz
WORKDIR actor-framework-0.14.5
RUN ./configure \
	--no-examples \
	--no-opencl \
	--with-gcc=/usr/bin/g++-6
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

# Remove sources
RUN rm -rf /scratch

RUN mkdir /opt/connector
COPY requirements.txt /opt/connector/.

WORKDIR /opt/connector

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

EXPOSE 8080

# copy stuff from _within_ src & conf to /opt/connector (note the trailing slash after conf)
COPY src/ /opt/connector

COPY conf/ /opt/connector

ENTRYPOINT ["/usr/bin/python","connector.py"]
