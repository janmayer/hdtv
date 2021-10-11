FROM rootproject/root:6.24.06-ubuntu20.04

RUN apt-get update -y && apt-get install -y --no-install-recommends python3-pip==20.0.2 && rm -rf /var/lib/apt/lists/*
RUN pip3 install jupyter==1.0.0

WORKDIR /work
COPY . /work
RUN python3 setup.py install

RUN for extension in mfile-root fit display calibration; do \
    (cd "/usr/local/lib/python3.*/dist-packages/hdtv-*/hdtv/rootext/${extension}" && \
    cmake . -DCMAKE_INSTALL_PREFIX=/root/.cache/hdtv/$(ls /root/.cache/hdtv/) -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . --target install) \
  done

RUN python3 -c 'import hdtv'
RUN type hdtv
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8080", "--allow-root"]
