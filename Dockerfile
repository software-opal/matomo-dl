FROM ubuntu:latest
RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
  && rm -rf /var/lib/apt/lists/*
COPY . /code
RUN set -x \
  && mkdir /wheels \
  && pip3 wheel --no-cache-dir --wheel-dir /wheels /code \
  && true

FROM ubuntu:latest
RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
  && rm -rf /var/lib/apt/lists/*
RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    git \
  && rm -rf /var/lib/apt/lists/*
COPY --from=0 /wheels /wheels
RUN set -x \
  && pip3 install --no-cache-dir --no-index --find-links=/wheels matomo-dl \
  && rm -rf /wheels \
  && true
ENV PYTHONUNBUFFERED 1
ENTRYPOINT ['/usr/local/bin/matomo-dl']
CMD ['--help']
