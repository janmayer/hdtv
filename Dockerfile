FROM rootproject/root:6.34.00-ubuntu24.04

LABEL name="hdtv"

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends pipx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install

RUN python3 -m pipx install . && \
    hdtv --rebuild-usr

WORKDIR /work
CMD hdtv
