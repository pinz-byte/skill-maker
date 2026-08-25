#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# install-kiro-skills.sh — Sync skills from pinz-byte/skill-maker to Kiro
# ─────────────────────────────────────────────────────────────────────────────
# Usage:
#   ./install-kiro-skills.sh              # Install all 85 skills globally
#   ./install-kiro-skills.sh --core       # Install only core/universal skills
#   ./install-kiro-skills.sh --list       # List available skills
#   ./install-kiro-skills.sh --workspace  # Install core skills into current project's .kiro/
#   ./install-kiro-skills.sh skill-name   # Install a specific skill
#
# Team setup:
#   curl -sSL https://raw.githubusercontent.com/pinz-byte/skill-maker/main/install-kiro-skills.sh | bash
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_URL="https://github.com/pinz-byte/skill-maker.git"
KIRO_SKILLS_DIR="${HOME}/.kiro/skills"
TMP_DIR="/tmp/kiro-skills-sync-$$"
VERSION="1.0.0"

# ─── Core skills: universal, team-safe, no project-specific dependencies ─────
CORE_SKILLS=(
  critical-thinker
  creative-thinker
  logic-thinker
  loop-breaker
  git-ops
  self-audit
  auditor-general
  verify-loop
  phased-deploy
  continuity-seed
  reentry
  session-bootstrap
  projectmd-gen
  projectmd-optimizer
  project-init
  meta-no-bare-names
  dependency-audit
  forensic-auditor
  data-analyst
  masterkey
  ib
  ceo-planner
  work-retrospective
  builder-handoff
  offload
  ultrathink
  toolbox
)

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log()   { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
err()   { echo -e "${RED}✗${NC} $1" >&2; }
info()  { echo -e "${BLUE}→${NC} $1"; }
header(){ echo -e "\n${BOLD}$1${NC}"; }

# ─── Functions ────────────────────────────────────────────────────────────────

clone_repo() {
  if [ -d "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
  fi
  info "Cloning skill-maker repo..."
  git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR" 2>/dev/null || {
    err "Failed to clone repo. Check network and access to $REPO_URL"
    exit 1
  }
}

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

list_skills() {
  clone_repo
  header "Available Skills ($(find "$TMP_DIR" -maxdepth 2 -name 'SKILL.md' | wc -l | tr -d ' ') total)"
  echo ""
  printf "%-30s %s\n" "SKILL" "INTENT"
  printf "%-30s %s\n" "-----" "------"
  for dir in "$TMP_DIR"/*/SKILL.md; do
    skill=$(basename "$(dirname "$dir")")
    intent=$(grep -A1 "metadata:" "$dir" 2>/dev/null | grep "intent:" | sed 's/.*intent: *//' || echo "—")
    printf "%-30s %s\n" "$skill" "$intent"
  done | sort
  echo ""
  info "Core skills (--core): ${#CORE_SKILLS[@]} skills"
}

install_skill() {
  local skill_name="$1"
  local target_dir="$2"
  local source="$TMP_DIR/$skill_name"

  if [ ! -f "$source/SKILL.md" ]; then
    warn "Skill '$skill_name' not found in repo — skipping"
    return 1
  fi

  mkdir -p "$target_dir/$skill_name"
  cp "$source/SKILL.md" "$target_dir/$skill_name/SKILL.md"

  # Copy references, scripts, evals if present
  for subdir in references scripts evals; do
    if [ -d "$source/$subdir" ]; then
      cp -r "$source/$subdir" "$target_dir/$skill_name/"
    fi
  done

  return 0
}

install_all() {
  local target="${1:-$KIRO_SKILLS_DIR}"
  clone_repo

  header "Installing all skills to $target"
  mkdir -p "$target"

  local count=0
  local failed=0
  for dir in "$TMP_DIR"/*/SKILL.md; do
    skill=$(basename "$(dirname "$dir")")
    if install_skill "$skill" "$target"; then
      count=$((count + 1))
    else
      failed=$((failed + 1))
    fi
  done

  echo ""
  log "Installed $count skills to $target"
  [ $failed -gt 0 ] && warn "$failed skills failed"
  info "Skills are active immediately — use /skill-name or trigger phrases"
}

install_core() {
  local target="${1:-$KIRO_SKILLS_DIR}"
  clone_repo

  header "Installing ${#CORE_SKILLS[@]} core skills to $target"
  mkdir -p "$target"

  local count=0
  for skill in "${CORE_SKILLS[@]}"; do
    if install_skill "$skill" "$target"; then
      count=$((count + 1))
    fi
  done

  echo ""
  log "Installed $count core skills to $target"
  info "Skills are active immediately — use /skill-name or trigger phrases"
}

install_workspace() {
  local ws_skills=".kiro/skills"

  if [ ! -d ".git" ]; then
    err "Not in a git repository. Run this from your project root."
    exit 1
  fi

  clone_repo
  header "Installing core skills to workspace ($ws_skills/)"
  mkdir -p "$ws_skills"

  local count=0
  for skill in "${CORE_SKILLS[@]}"; do
    if install_skill "$skill" "$ws_skills"; then
      count=$((count + 1))
    fi
  done

  echo ""
  log "Installed $count core skills to $ws_skills/"
  info "Commit with: git add .kiro/skills && git commit -m 'feat: add team kiro skills'"
  info "Team members get these skills automatically when they open the project"
}

install_single() {
  local skill_name="$1"
  local target="${2:-$KIRO_SKILLS_DIR}"
  clone_repo

  mkdir -p "$target"
  if install_skill "$skill_name" "$target"; then
    log "Installed '$skill_name' to $target/$skill_name/"
  else
    err "Skill '$skill_name' not found"
    exit 1
  fi
}

show_help() {
  cat << 'EOF'

  ┌─────────────────────────────────────────────┐
  │  install-kiro-skills.sh                     │
  │  Sync skills from pinz-byte/skill-maker     │
  └─────────────────────────────────────────────┘

  USAGE:
    ./install-kiro-skills.sh [OPTION|SKILL_NAME]

  OPTIONS:
    (none)        Install all 85 skills globally (~/.kiro/skills/)
    --core        Install 27 core/universal skills globally
    --workspace   Install core skills into current project (.kiro/skills/)
    --list        List all available skills
    --help        Show this help

  EXAMPLES:
    # Full install for power users
    ./install-kiro-skills.sh

    # Just the essentials
    ./install-kiro-skills.sh --core

    # Share with your team via git
    cd ~/my-project
    ./install-kiro-skills.sh --workspace
    git add .kiro/skills && git commit -m "feat: add team skills"

    # Install one specific skill
    ./install-kiro-skills.sh critical-thinker

    # Remote install (no clone needed)
    curl -sSL https://raw.githubusercontent.com/pinz-byte/skill-maker/main/install-kiro-skills.sh | bash

  LOCATIONS:
    ~/.kiro/skills/    Global (all projects, IDE + CLI only)
    .kiro/skills/      Workspace (this project, all surfaces)

  Workspace skills take priority over global when names collide.

EOF
}

# ─── Main ─────────────────────────────────────────────────────────────────────

case "${1:-}" in
  --help|-h)
    show_help
    ;;
  --list|-l)
    list_skills
    ;;
  --core|-c)
    install_core
    ;;
  --workspace|-w)
    install_workspace
    ;;
  "")
    install_all
    ;;
  *)
    install_single "$1"
    ;;
esac
