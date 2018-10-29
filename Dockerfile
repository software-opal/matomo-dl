FROM ubuntu:latest
RUN set -x \
  && apt-get update \
  && apt-get install -y \
    python3 \
    python3-pip \
    python3-wheel \
  && rm -rf /var/lib/apt/lists/*
COPY . /code
RUN set -x \
  && mkdir /wheels \
  && pip wheel --no-cache-dir --wheel-dir /wheels \
    /code \
    pip \
    setuptools \
    wheel \
  && true

FROM ubuntu:latest
RUN set -x \
  && apt-get update \
  && apt-get install -y \
    python3 \
    python3-pip \
    python3-wheel \
  && rm -rf /var/lib/apt/lists/*
COPY --from=0 /wheels /wheels
RUN set -x \
  && pip install --no-cache-dir --no-index --find-links=/wheels
    pip \
    wheel \
    setuptools \
  && pip install --no-cache-dir --no-index --find-links=/wheels
    matomo-dl \
  && rm -rf /wheels
  && true
ENV PYTHONUNBUFFERED 1
ENTRYPOINT ['/usr/local/bin/matomo-dl']
CMD ['--help']
