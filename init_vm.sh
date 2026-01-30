#!/bin/bash
# =============================================================================
# Project Prism - One-Time VM Bootstrap Script
# Fully automated - no prompts
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo ""
echo "=============================================="
echo "   Project Prism - VM Bootstrap Script"
echo "   Fully Automated Setup"
echo "=============================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root."
    SUDO=""
else
    SUDO="sudo"
fi

# Step 1: Install prerequisites (no update/upgrade)
print_status "Installing prerequisites..."
$SUDO apt-get install -y -qq \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git > /dev/null 2>&1
print_success "Prerequisites installed!"

# Step 2: Install Docker Engine
print_status "Installing Docker Engine..."

# Detect OS and Codename
OS_ID=$(grep -oP '^ID=\K\w+' /etc/os-release)
CODENAME=$(grep -oP '^VERSION_CODENAME=\K\w+' /etc/os-release)

if [[ "$OS_ID" != "ubuntu" && "$OS_ID" != "debian" ]]; then
    print_warning "OS is $OS_ID. Using Debian as fallback..."
    OS_ID="debian"
fi

print_status "Detected OS: $OS_ID ($CODENAME)"

# Add Docker's official GPG key (force overwrite, no prompt)
$SUDO install -m 0755 -d /etc/apt/keyrings
$SUDO rm -f /etc/apt/keyrings/docker.gpg
curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
$SUDO chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_ID \
  $CODENAME stable" | \
  $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
$SUDO apt-get update -qq > /dev/null 2>&1
$SUDO apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1

# Add current user to docker group (if not root)
if [ "$EUID" -ne 0 ]; then
    $SUDO usermod -aG docker $USER
    print_warning "Added $USER to docker group. Log out and back in for this to take effect."
fi

print_success "Docker Engine installed!"

# Verify Docker installation
print_status "Verifying Docker installation..."
docker --version
docker compose version
print_success "Docker is working!"

# Step 3: Setup Project Directory (fully automated - use public HTTPS)
PROJECT_DIR="$HOME/project-prism"
print_status "Setting up project directory at $PROJECT_DIR..."

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists. Pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    print_status "Cloning repository (public HTTPS)..."
    git clone https://github.com/pratikh6i/project-prism.git "$PROJECT_DIR"
fi

print_success "Project directory setup complete!"

# Step 4: Make scripts executable
print_status "Setting script permissions..."
chmod +x "$PROJECT_DIR/scripts/vm_update.sh"
print_success "Scripts are now executable!"

# Step 5: Create data and logs directories
print_status "Creating persistent data directories..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"
print_success "Data directories created!"

# Step 6: Generate SSH key for GitHub Deploy Keys (if not exists)
print_status "Checking SSH key for CI/CD..."
SSH_KEY_PATH="$HOME/.ssh/id_rsa"

if [ ! -f "$SSH_KEY_PATH" ]; then
    print_status "Generating new SSH key..."
    mkdir -p "$HOME/.ssh"
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "project-prism-deploy@$(hostname)"
    print_success "SSH key generated!"
else
    print_success "SSH key already exists!"
fi

# Step 7: Build and start the application
print_status "Building and starting Project Prism..."
cd "$PROJECT_DIR"
docker compose up -d --build

# Get VM's public IP
print_status "Fetching VM's public IP..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || curl -s ifconfig.me || echo "Unable to detect")

# Final Output
echo ""
echo "=============================================="
echo -e "${GREEN}   SETUP COMPLETE!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}Application URL:${NC} http://$PUBLIC_IP:8501"
echo ""
echo -e "${BLUE}SSH Public Key (for GitHub CI/CD):${NC}"
echo "----------------------------------------------"
cat "$SSH_KEY_PATH.pub"
echo "----------------------------------------------"
echo ""
echo -e "${YELLOW}TO ENABLE AUTOMATIC CI/CD DEPLOYMENTS:${NC}"
echo ""
echo "1. Add the following secrets to your GitHub repository:"
echo "   → Go to: https://github.com/pratikh6i/project-prism/settings/secrets/actions"
echo "   → Add these secrets:"
echo "     • VM_HOST: $PUBLIC_IP"
echo "     • VM_USERNAME: $USER"
echo "     • SSH_KEY: (run 'cat ~/.ssh/id_rsa' and paste the output)"
echo ""
echo -e "${GREEN}🚀 Your app is now running at: http://$PUBLIC_IP:8501${NC}"
echo ""
