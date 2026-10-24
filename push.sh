#!/bin/bash
# Hes Projects ® by FePe - CodeLab HU GitHub Push
# Copyright (C) 2024-2026 Péter Felhősi

set -e

MESSAGE=${1:-"update: CodeLab HU"}
TAG=${2:-""}

echo "© Hes Projects ® by FePe - CodeLab HU - GitHub Push"
echo "Üzenet: $MESSAGE"
if [ -n "$TAG" ]; then
  echo "Tag: $TAG"
fi

# Git init ha nincs
if [ ! -d ".git" ]; then
  echo "Git init..."
  git init
  git branch -M main
fi

# Add all
git add .

# Commit
git commit -m "$MESSAGE - Hes Projects ® by FePe - GNU GPL v3" || echo "Nincs változás vagy már commitolva"

# Tag ha van
if [ -n "$TAG" ]; then
  git tag -a "$TAG" -m "$MESSAGE - $TAG - Hes Projects ® by FePe" || echo "Tag már létezik"
  echo "Tag létrehozva: $TAG"
fi

# Push
echo "Push main..."
git push origin main || git push -u origin main || echo "Push hiba - állítsd be a remote-ot: git remote add origin <url>"

if [ -n "$TAG" ]; then
  echo "Push tag..."
  git push origin "$TAG" || echo "Tag push hiba"
fi

echo "✅ Kész! Hes Projects ® by FePe"
echo "GitHub: https://github.com/<user>/codelab-hu"
