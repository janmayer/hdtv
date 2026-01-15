FROM rootproject/root:6.34.00-ubuntu24.04

LABEL name="hdtv"

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends pipx xvfb && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install

RUN bash -c "Xvfb :99 -screen 0 1024x768x16 &" && \
    python3 -m pipx install . && \
    DISPLAY=:99 hdtv --rebuild-usr --execute exit

WORKDIR /work
CMD hdtv
