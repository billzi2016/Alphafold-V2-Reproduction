FROM python:3.11-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt /tmp/base.txt
RUN pip install --no-cache-dir -r /tmp/base.txt

COPY pyproject.toml README.md /workspace/
COPY src /workspace/src

ENV PYTHONPATH=/workspace/src

CMD ["python3", "-m", "af2_repro.cli.predict", "--help"]
