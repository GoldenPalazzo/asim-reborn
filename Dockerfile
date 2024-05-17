FROM ubuntu:22.04
ENV DOCKER_UID=1000
ENV DOCKER_GID=1000

ENV VBCC=/opt/vbcc
ENV PATH=/opt/vbcc/bin:"$PATH"

RUN echo "$DOCKER_UID"
RUN addgroup --gid "$DOCKER_GID" group
RUN adduser --ingroup group --disabled-password --uid "$DOCKER_UID" user
RUN apt update && apt install -y wget tar
RUN cd /opt/ && \
    wget http://www.ibaug.de/vbcc/vbcc_linux_x64.tar.gz -O - | tar xz
RUN apt install -y binutils-m68k-linux-gnu bsdmainutils
USER user
WORKDIR /srv
CMD ["/bin/bash"]
