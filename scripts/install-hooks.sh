#!/bin/sh
# Point git at the repo's hooks folder (this repo only).
set -eu
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
echo "Git hooks installed from .githooks/"
