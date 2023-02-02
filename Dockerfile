FROM rootproject/root:6.26.10-ubuntu22.04

RUN apt-get update -y &&\
    apt-get install -y --no-install-recommends python3-pip xvfb &&\
    rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install
RUN python3 setup.py install
RUN bash -c "Xvfb :0 -screen 0 1024x768x16 &" &&\
    DISPLAY=:0 hdtv --rebuild-usr

WORKDIR /work
CMD hdtv
