FROM alpine:3.3
# Use this for raspberry
#FROM hypriot/rpi-alpine-scratch:latest

RUN apk upgrade

RUN apk add --update \
    build-base \
    alpine-sdk \
    curl \
    curl-dev \
    libev \
    glib-dev \
    loudmouth-dev \
    libnetfilter_queue \
    libnl \
    libpcap \
    libtool \
    udns-dev \
    python3 \
    python3-dev \
    automake \
    libnl3-dev \
    libev-dev

# get pip3 (bug from last week: https://bugs.alpinelinux.org/issues/5103)
RUN python3 -m ensurepip

# we seem to need this (capital "C"ython, has deprecated distutils, alpine package doesnt!)
RUN pip3 install --upgrade pip Cython

# alpine py-yaml does not provide wanted site packages.
RUN pip3 install --upgrade pyyaml


RUN mkdir -p /opt/dionaea /opt/libemu

# libemu manual build:

RUN git clone https://github.com/buffer/libemu.git /opt/libemu
WORKDIR /opt/libemu
RUN autoreconf -vi
RUN ./configure --prefix=/usr
RUN make install


# dionaea build:

RUN git clone -b '0.6.0' https://github.com/DinoTools/dionaea.git /opt/dionaea
WORKDIR /opt/dionaea
RUN autoreconf -vif
RUN ./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --localstatedir=/var/lib/dionaea \
    --enable-pcap \
    --with-pcap-lib=/usr/lib \
    --with-pcap-include=/usr/include \
    --enable-netfilter_queue \
    --enable-nl \
    --disable-werror \
    --with-python=/usr/bin/python3 \
    --with-cython-dir=/usr/bin \
    --with-ev-include=/usr/include \
    --with-ev-lib=/usr/lib \
    --with-emu-lib=/usr/lib/libemu \
    --with-emu-include=/usr/include \
    --with-nl-lib=/usr/lib \
    --with-nl-include=/usr/include/libnl3
RUN make
RUN make install


RUN rm /etc/dionaea/ihandlers-enabled/*
RUN rm /etc/dionaea/services-enabled/*
RUN mkdir -p /var/dionaea/logs/
RUN mkdir -p /etc/dionaea/services-enabled /etc/dionaea/ihandlers-enabled
RUN mkdir -p /var/dionaea/roots/ftp /var/dionaea/roots/www
RUN mkdir -p /var/dionaea/streams /var/dionaea/binaries

# http, https
EXPOSE 80
EXPOSE 443
# ftp
EXPOSE 21
# mysql
EXPOSE 3306
# smb
EXPOSE 445

COPY dionaea.conf /etc/dionaea/dionaea.conf
COPY services/ /etc/dionaea/services-enabled/
COPY ihandlers/ /etc/dionaea/ihandlers-enabled/

CMD dionaea -l all,-debug -L '*' -c /etc/dionaea/dionaea.conf
