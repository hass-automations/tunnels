# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache \
    bash \
    python3 \
    py3-flask \
    wireguard-tools \
    iproute2 \
    iptables \
    openresolv \
    curl

# Build amneziawg-go (userspace, no kernel module needed) and awg/awg-quick from master.
# Master is required: server runs AmneziaWG 2.0 with I1-I5 + HeaderProtectionKey params.
# libmnl stays installed after apk del because wireguard-tools depends on it at runtime.
RUN apk add --no-cache --virtual .awgbuild \
        go git make linux-headers libmnl-dev \
 && git clone --depth 1 https://github.com/amnezia-vpn/amneziawg-go /tmp/awg-go \
 && cd /tmp/awg-go && go build -ldflags="-s -w" -o /usr/bin/amneziawg-go . \
 && git clone --depth 1 https://github.com/amnezia-vpn/amneziawg-tools /tmp/awg-tools \
 && cd /tmp/awg-tools/src && make && make install PREFIX=/usr \
 && rm -rf /tmp/awg-go /tmp/awg-tools /root/go /root/.cache \
 && apk del .awgbuild

COPY run.sh /
COPY custom_components/tunnels /app
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
