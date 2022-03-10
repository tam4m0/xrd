#!/bin/sh

for p in *.py; do
    black $p;
    isort --profile black $p;
done;
