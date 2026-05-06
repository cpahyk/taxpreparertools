#!/bin/bash
# ============================================================
# TaxPreparerTools.com — GitHub Deploy Script
# Usage: bash deploy.sh YOUR_GITHUB_USERNAME
# ============================================================

set -e

USERNAME=$1

if [ -z "$USERNAME" ]; then
  echo ""
  echo "❌  Usage: bash deploy.sh YOUR_GITHUB_USERNAME"
  echo "    Example: bash deploy.sh johndoe"
  echo ""
  exit 1
fi

REPO="taxpreparertools"
REMOTE="https://github.com/$USERNAME/$REPO.git"

echo ""
echo "🚀  TaxPreparerTools.com GitHub Deployer"
echo "    Repo:  $REMOTE"
echo "    User:  $USERNAME"
echo ""

# Init git if needed
if [ ! -d ".git" ]; then
  echo "📁  Initializing git repository..."
  git init
  git branch -M main
fi

# Set remote
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REMOTE"
  echo "🔗  Remote updated: $REMOTE"
else
  git remote add origin "$REMOTE"
  echo "🔗  Remote added: $REMOTE"
fi

# Stage and commit
echo "📦  Staging all files..."
git add -A

CHANGES=$(git diff --cached --name-only | wc -l | tr -d ' ')

if [ "$CHANGES" -eq "0" ]; then
  echo "✅  Nothing new to commit — already up to date."
else
  echo "💾  Committing $CHANGES changed file(s)..."
  git commit -m "Deploy: updated $(date '+%Y-%m-%d %H:%M') — $CHANGES files changed"
fi

# Push
echo "⬆️   Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅  DEPLOYED SUCCESSFULLY!"
echo ""
echo "    📌  GitHub repo:  https://github.com/$USERNAME/$REPO"
echo "    🌐  Live site:    https://$USERNAME.github.io/$REPO"
echo "    🔧  Pages setup:  https://github.com/$USERNAME/$REPO/settings/pages"
echo ""
echo "    ─────────────────────────────────────────────────────"
echo "    Next: Go to Settings → Pages → Source: main / root"
echo "    Then enable your custom domain (taxpreparertools.com)"
echo "    ─────────────────────────────────────────────────────"
echo ""
