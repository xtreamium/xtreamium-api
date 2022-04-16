#!/usr/bin/env bash

docker context use default

docker build \
  -t fergalmoran/xtreamium-backend \
  -f docker/Dockerfile .

docker push fergalmoran/xtreamium-backend
