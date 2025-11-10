LABEL name="hdtv"

FROM rootproject/root:6.28.04-ubuntu22.04

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install
RUN pip3 install "scipy>=1.9.0,<1.10.0" && \
    python3 setup.py install
RUN bash -c "Xvfb :0 -screen 0 1024x768x16 &" && \
    DISPLAY=:0 hdtv --execute exit

WORKDIR /work
CMD hdtv
