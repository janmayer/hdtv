FROM rootproject/root:6.34.00-ubuntu24.04

LABEL name="hdtv"

ENV PATH="/root/.local/bin:$PATH"
ENV DISPLAY=:99

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        pipx \
        xvfb \
        xauth \
        libx11-6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY . /install

RUN python3 -m pipx install .

WORKDIR /work

# Runtime entrypoint
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN /entrypoint.sh
RUN touch /root/.local/share/hdtv/hdtv_history
RUN chmod 777 /root/.local/share/hdtv/hdtv_history
CMD ["hdtv"]

