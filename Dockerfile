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

COPY run.sh /
COPY app /app
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
