#!/usr/bin/env bash
set -euo pipefail

urls=(
  "https://discord.com/assets/fae560804a8a5a01.css"
  "https://discord.com/assets/e545279a666109e6.css"
  "https://discord.com/assets/e264a21be8357746c.css"
  "https://discord.com/assets/b4d4206530cb9200.css"
  "https://discord.com/assets/a3463634181286d1.css"
  "https://discord.com/assets/a58a7444528e9503.css"
  "https://discord.com/assets/9693049372b373c7.css"
  "https://discord.com/assets/7527552610e2e234.css"
  "https://discord.com/assets/12633.c3d5ff6526d6e180.css"
  "https://discord.com/assets/7261a20bb7441aaa.css"
  "https://discord.com/assets/870ee4c4cf64e352.css"
  "https://discord.com/assets/5b76c661367676d6.css"
  "https://discord.com/assets/4a08f5367c32f956.css"
  "https://discord.com/assets/2f71c76a7938723b.css"
)

mkdir -p downloaded_css

for u in "${urls[@]}"; do
  fname=$(basename "$u")
  out="downloaded_css/$fname"
  echo "Downloading $fname..."
  if curl -fSL --retry 3 --retry-delay 2 --compressed "$u" -o "$out"; then
    echo "  saved to $out"
  else
    echo "  failed to download $fname" >&2
  fi
done

