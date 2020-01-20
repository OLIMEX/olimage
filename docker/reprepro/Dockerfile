FROM debian:latest
MAINTAINER Stefan Mavrodiev <stefan@olimex.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
        gnupg2 reprepro && \
    rm -rf /var/cache/apt/*

ENV REPREPRO_BASE_DIR /var/reprepro/debian

# Generate keys
ADD batch.gpg ./
RUN gpg2 --batch --generate-key batch.gpg
