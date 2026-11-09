#!/bin/sh
# Rebuild website/d3.min.js (the d3 modules the page's charts draw with) and website/d3-LICENSE.txt.
# One command, from anywhere: tools/d3/build.sh [path/to/website]
# The versions are pinned in package.json and package-lock.json; install scripts are not run.
set -e
here=$(cd "$(dirname "$0")" && pwd)
site=$(cd "${1:-$here/../../website}" && pwd)
cd "$here"
npm ci --ignore-scripts --no-audit --no-fund --loglevel=error
node build.mjs "$site"
