#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d .git ]; then
  echo "❌ Esto no parece un repositorio Git."
  exit 1
fi

chmod +x .githooks/commit-msg
git config core.hooksPath .githooks
echo "🤖 Guardián de commits instalado."