FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    coreutils \
    curl \
    findutils \
    git \
    grep \
    procps \
    python3 \
    python3-pip \
    tar \
    xz-utils \
  && ln -sf /usr/bin/python3 /usr/local/bin/python \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain none

ENV PATH="/root/.elan/bin:${PATH}"
WORKDIR /workspace/lean-time-horizon

COPY . /workspace/lean-time-horizon

RUN elan toolchain install "$(cat lean-toolchain)" \
  && lake exe cache get \
  && lake build \
  && python scripts/export_public_tasks.py --out public_tasks \
  && python scripts/validate_public_export.py --out public_tasks \
  && mkdir -p /opt/lean-time-horizon-private \
  && python scripts/generate_taiga_hidden_bundle.py --out /opt/lean-time-horizon-private/hidden_bundle.json \
  && chmod 700 /opt/lean-time-horizon-private \
  && rm -rf tasks transcripts tmp

ENV LEAN_TIME_HORIZON_ROOT=/workspace/lean-time-horizon
ENV TAIGA_WORKDIR=/workdir
ENV TAIGA_HIDDEN_BUNDLE=/opt/lean-time-horizon-private/hidden_bundle.json
ENV TAIGA_DELETE_HIDDEN_BUNDLE=1

RUN mkdir -p /workdir /etc/ssl/certs /usr/local/share/ca-certificates \
  && touch /usr/local/share/ca-certificates/custom-ca.crt

CMD ["python", "-u", "/workspace/lean-time-horizon/taiga/mcp_server.py"]
