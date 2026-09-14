# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM

# Alpine 3.15 ships Go 1.17 which can't parse go.mod with 'go 1.25.0'.
# Use official golang image as a build stage, copy only the final binaries.
FROM golang:1.25-alpine AS awgbuilder
RUN apk add --no-cache git make linux-headers libmnl-dev \
 && git clone --depth 1 https://github.com/amnezia-vpn/amneziawg-go /tmp/awg-go \
 && cd /tmp/awg-go && go build -ldflags="-s -w" -o /usr/bin/amneziawg-go . \
 && git clone --depth 1 https://github.com/amnezia-vpn/amneziawg-tools /tmp/awg-tools \
 && cd /tmp/awg-tools/src && make && make install PREFIX=/usr

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

COPY --from=awgbuilder /usr/bin/amneziawg-go /usr/bin/amneziawg-go
COPY --from=awgbuilder /usr/bin/awg          /usr/bin/awg
COPY --from=awgbuilder /usr/bin/awg-quick    /usr/bin/awg-quick

COPY run.sh /
COPY custom_components/tunnels /app
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
