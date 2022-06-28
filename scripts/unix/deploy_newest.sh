#!/bin/bash

git fetch --all

git reset --hard origin/main

chmod +x ./scripts/unix/*.sh

./scripts/unix/run_prod.sh