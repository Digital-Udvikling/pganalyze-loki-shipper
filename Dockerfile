FROM python:3.12 AS rye-builder

RUN \
  --mount=type=cache,target=/var/lib/apt/lists \
  --mount=type=cache,target=/var/cache/apt/archives \
  apt-get update \
  && apt-get install -y --no-install-recommends build-essential

ENV RYE_HOME="/work/rye"
ENV PATH="$RYE_HOME/shims:$PATH"

WORKDIR /app
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION=--yes bash

#COPY requirements.lock pyproject.toml README.md /app/
#RUN $HOME/.rye/shims/rye sync
#COPY . /app
#RUN rye build --wheel --clean

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=src,target=src \
    --mount=type=cache,target=/work.cache/pip \
    # install proeject prod deps
    rye sync --no-dev --no-lock \
    && rye build --all --wheel

FROM python:slim

COPY --from=rye-builder /app/dist /dist
RUN pip install --no-cache-dir /dist/*.whl
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir /dist/*.whl
CMD python -m pganalyze_loki_shipper