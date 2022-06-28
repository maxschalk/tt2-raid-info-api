#!/bin/bash

source ./venv/bin/activate

uvicorn src.app.main:app --host 0.0.0.0 --port 80