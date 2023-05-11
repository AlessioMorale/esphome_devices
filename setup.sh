#!/bin/bash
set -ex
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -U
