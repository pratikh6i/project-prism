#!/bin/bash
# =============================================================================
# Project Prism - One-Time VM Bootstrap Script
# Run this script ONCE on a fresh Ubuntu 22.04 LTS VM
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo ""
echo "=============================================="
echo "   Project Prism - VM Bootstrap Script"
echo "   For Ubuntu 22.04 LTS on GCP"
echo "=============================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Some commands will be adjusted."
    SUDO=""
else
    SUDO="sudo"
fi

# Step 1: System Update
print_status "Updating system packages..."
$SUDO apt-get update -y
$SUDO apt-get upgrade -y
print_success "System packages updated!"

# Step 2: Install prerequisites
print_status "Installing prerequisites..."
$SUDO apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git
print_success "Prerequisites installed!"

# Step 3: Install Docker Engine
print_status "Installing Docker Engine..."

# Detect OS and Codename
OS_ID=$(grep -oP '^ID=\K\w+' /etc/os-release)
CODENAME=$(grep -oP '^VERSION_CODENAME=\K\w+' /etc/os-release)

if [[ "$OS_ID" != "ubuntu" && "$OS_ID" != "debian" ]]; then
    print_warning "OS is $OS_ID. Attempting to use Debian-style installation as fallback..."
    OS_ID="debian"
fi

print_status "Detected OS: $OS_ID ($CODENAME)"

# Add Docker's official GPG key
$SUDO install -m 0755 -d /etc/apt/keyrings
curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
$SUDO chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_ID \
  $CODENAME stable" | \
  $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
$SUDO apt-get update -y
$SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group (if not root)
if [ "$EUID" -ne 0 ]; then
    $SUDO usermod -aG docker $USER
    print_warning "Added $USER to docker group. You may need to log out and back in for this to take effect."
fi

print_success "Docker Engine installed!"

# Verify Docker installation
print_status "Verifying Docker installation..."
docker --version
docker compose version
print_success "Docker is working!"

# Step 4: Setup Project Directory
PROJECT_DIR="$HOME/project-prism"
print_status "Setting up project directory at $PROJECT_DIR..."

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists. Pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    print_status "Cloning repository..."
    echo ""
    
    # Prompt for clone method
    echo "Choose clone method:"
    echo "  1) HTTPS (requires PAT for private repos)"
    echo "  2) SSH (requires SSH key in GitHub)"
    echo "  3) Public HTTPS (no authentication)"
    read -p "Enter choice [1-3]: " clone_choice
    
    case $clone_choice in
        1)
            read -p "Enter your GitHub Personal Access Token (PAT): " -s github_pat
            echo ""
            git clone https://${github_pat}@github.com/pratikh6i/project-prism.git "$PROJECT_DIR"
            ;;
        2)
            git clone git@github.com:pratikh6i/project-prism.git "$PROJECT_DIR"
            ;;
        3|*)
            git clone https://github.com/pratikh6i/project-prism.git "$PROJECT_DIR"
            ;;
    esac
fi

print_success "Project directory setup complete!"

# Step 5: Make scripts executable
print_status "Setting script permissions..."
chmod +x "$PROJECT_DIR/scripts/vm_update.sh"
print_success "Scripts are now executable!"

# Step 6: Create data and logs directories if they don't exist
print_status "Creating persistent data directories..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"
print_success "Data directories created!"

# Step 7: Generate SSH key for GitHub Deploy Keys (if not exists)
print_status "Checking SSH key for GitHub Deploy Keys..."
SSH_KEY_PATH="$HOME/.ssh/id_rsa"

if [ ! -f "$SSH_KEY_PATH" ]; then
    print_status "Generating new SSH key..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "project-prism-deploy@$(hostname)"
    print_success "SSH key generated!"
else
    print_success "SSH key already exists!"
fi

# Get VM's public IP
print_status "Fetching VM's public IP..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || curl -s ifconfig.me || echo "Unable to detect")

# Final Output
echo ""
echo "=============================================="
echo -e "${GREEN}   SETUP COMPLETE!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}VM Public IP:${NC} $PUBLIC_IP"
echo ""
echo -e "${BLUE}SSH Public Key (for GitHub Deploy Keys):${NC}"
echo "----------------------------------------------"
cat "$SSH_KEY_PATH.pub"
echo "----------------------------------------------"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Add the SSH public key above to your GitHub repository:"
echo "   → Go to: https://github.com/pratikh6i/project-prism/settings/keys"
echo "   → Click 'Add deploy key'"
echo "   → Paste the key above and give it a title like 'GCP VM Deploy Key'"
echo "   → Check 'Allow write access' if needed"
echo ""
echo "2. Add the following secrets to your GitHub repository:"
echo "   → Go to: https://github.com/pratikh6i/project-prism/settings/secrets/actions"
echo "   → Add these secrets:"
echo "     • VM_HOST: $PUBLIC_IP"
echo "     • VM_USERNAME: $USER"
echo "     • SSH_KEY: (paste your PRIVATE key from ~/.ssh/id_rsa)"
echo ""
echo "3. Start the application:"
echo "   cd ~/project-prism"
echo "   docker compose up -d --build"
echo ""
echo "4. Access the application at:"
echo "   http://$PUBLIC_IP:8501"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
echo ""
