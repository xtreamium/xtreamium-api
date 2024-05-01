#!/usr/bin/env bash

docker context use default

docker build \
  -t ghcr.io/xtreamium/xtreamium-backend \
  -f docker/Dockerfile .

docker push ghcr.io/xtreamium/xtreamium-backend
