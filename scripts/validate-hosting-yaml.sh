#!/usr/bin/env bash
# Validate every example's hosting.yaml against the schema Hosting publishes for the version it declares.
# Run from the repository root: scripts/validate-hosting-yaml.sh (needs curl and uvx).
set -euo pipefail

schemas="https://hosting.haak.co/api/v1/hosting/schemas"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

for doc in */hosting.yaml; do
  version=$(sed -nE 's/^version: *"?([0-9]+\.[0-9]+)"?.*/\1/p' "$doc")
  if [ -z "$version" ]; then
    echo "::error file=$doc::no top-level version"
    exit 1
  fi
  code=$(curl -sS -o "$work/$version.json" -w '%{http_code}' "$schemas/$version")
  if [ "$code" != 200 ]; then
    echo "::error file=$doc::schema $version answered HTTP $code from $schemas/$version"
    exit 1
  fi
  uvx --quiet check-jsonschema@0.39.0 --schemafile "$work/$version.json" "$doc"
done
