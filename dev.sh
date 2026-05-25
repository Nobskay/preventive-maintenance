#!/usr/bin/env bash
# ================================================================
# Predictive Maintenance System - Local Development Startup
# ================================================================
# Usage:
#   ./dev.sh          - Start backend + frontend in dev mode
#   ./dev.sh seed     - Seed the database with sample data
#   ./dev.sh docker   - Start full stack with Docker Compose
#   ./dev.sh down     - Stop Docker Compose services
# ================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
DOCKER_DIR="$PROJECT_ROOT/docker"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[maintainiq]${NC} $1"; }
warn() { echo -e "${YELLOW}[maintainiq]${NC} $1"; }
err() { echo -e "${RED}[maintainiq]${NC} $1"; }

check_deps() {
    local missing=()
    command -v python3 &>/dev/null || command -v python &>/dev/null || missing+=("python")
    command -v node &>/dev/null || missing+=("node")
    command -v npm &>/dev/null || missing+=("npm")
    if [ ${#missing[@]} -gt 0 ]; then
        err "Missing dependencies: ${missing[*]}"
        exit 1
    fi
}

PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)

# ---- Commands ----

cmd_seed() {
    log "Seeding database with industrial sample data..."
    cd "$BACKEND_DIR"
    $PYTHON -m app.seed_data
    log "Seed complete."
}

cmd_docker() {
    log "Starting full stack with Docker Compose..."
    cd "$DOCKER_DIR"
    docker-compose up --build
}

cmd_down() {
    log "Stopping Docker Compose services..."
    cd "$DOCKER_DIR"
    docker-compose down
}

cmd_dev() {
    check_deps

    log "Starting Predictive Maintenance System in dev mode..."
    echo ""
    echo -e "  ${CYAN}Backend${NC}   → http://localhost:8000"
    echo -e "  ${CYAN}Frontend${NC}  → http://localhost:5173"
    echo -e "  ${CYAN}Swagger${NC}   → http://localhost:8000/docs"
    echo ""

    # Start backend in background
    log "Starting backend (FastAPI)..."
    cd "$BACKEND_DIR"
    $PYTHON -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    # Start frontend
    log "Starting frontend (Vite)..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!

    # Handle shutdown
    trap "log 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

    log "Both services started. Press Ctrl+C to stop."
    wait
}

# ---- Main ----

case "${1:-dev}" in
    seed)   cmd_seed ;;
    docker) cmd_docker ;;
    down)   cmd_down ;;
    dev)    cmd_dev ;;
    *)
        echo "Usage: $0 {dev|seed|docker|down}"
        exit 1
        ;;
esac
