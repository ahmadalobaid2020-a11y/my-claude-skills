#!/bin/sh
# Chromium wrapper for puppeteer in cloud containers: runs as root (needs --no-sandbox) and has no GPU
# (WebGL through SwiftShader). Use: PUPPETEER_EXECUTABLE_PATH=/path/to/chrome-nosandbox.sh node snap.mjs ...
# CHROME_BIN picks the browser; default is the Playwright Chromium that Claude Code cloud sessions ship.
exec "${CHROME_BIN:-/opt/pw-browsers/chromium}" --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader "$@"
