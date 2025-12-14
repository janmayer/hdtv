FROM rootproject/root:6.34.00-ubuntu24.04

LABEL name="hdtv"

ENV PATH="$PATH:/root/.local/bin"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends pipx xvfb && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install

RUN python3 -m pipx install . && \
    bash -c "Xvfb :0 -screen 0 1024x768x16 &" && \
    DISPLAY=:0 hdtv --rebuild-usr --execute exit

WORKDIR /work
CMD hdtv
