FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
  vim git curl \
  python3 \
  python3-pip \
  python3-dev \
  python3-matplotlib \
  python3-numpy \
  pylint \
  gcc \
  locales \
  fonts-ipafont-gothic fonts-ipafont-mincho \
  && locale-gen ja_JP.UTF-8 \
  && update-locale LANG=ja_JP.UTF-8

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=ja_JP.UTF-8

COPY .vimrc /root/.vimrc
