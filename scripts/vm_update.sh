#!/bin/bash
# =============================================================================
# Project Prism - VM Update Script
# This script is executed by GitHub Actions CI/CD Pipeline
# =============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
PROJECT_DIR="$HOME/project-prism"
DEPLOY_LOG="$PROJECT_DIR/deploy.log"

# Function to log messages
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$DEPLOY_LOG"
}

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "Error: Project directory not found!"; exit 1; }

log "=========================================="
log "Starting deployment process..."
log "=========================================="

# Pull latest code from main branch
log "Pulling latest changes from Git..."
git pull origin main

# Rebuild and restart containers
log "Rebuilding Docker containers..."
docker compose up -d --build

# Clean up unused images to save disk space
log "Cleaning up unused Docker resources..."
docker system prune -f

# Log completion
log "Deployment completed successfully!"
log "=========================================="

# Display running containers
docker ps --filter "name=prism"

echo ""
echo "✅ Deployment finished at $(date)"
