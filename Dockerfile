FROM python:3.7-alpine

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=0.12.11

COPY . ./

# System deps:
RUN apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
            --update --no-cache python3-dev libgfortran && \
    apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
            --update --no-cache py-numpy-dev && \
    apk add --update --no-cache build-base libstdc++ git \
                                libpng libpng-dev \
                                freetype freetype-dev && \
    # Update musl to workaround a bug
    apk upgrade --repository http://dl-cdn.alpinelinux.org/alpine/edge/main musl && \
    # Install poetry and dependencies
    pip install "poetry==$POETRY_VERSION" && \
    poetry config settings.virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi && \
    # Cleanup
    apk del --purge build-base libgfortran libpng-dev freetype-dev \
                    python3-dev py-numpy-dev && \
    rm -vrf /var/cache/apk/*
