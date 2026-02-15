#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║   TeamFlow VPS Deploy Script v1.0    ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Step 1: Install Docker
echo -e "${YELLOW}[1/6] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Step 2: Install Docker Compose
echo -e "${YELLOW}[2/6] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Step 3: Setup project directory
echo -e "${YELLOW}[3/6] Setting up project...${NC}"
PROJECT_DIR="/opt/teamflow"

if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p $PROJECT_DIR
fi

cd $PROJECT_DIR

# Check if archive exists in current directory
if [ -f "$HOME/teamflow-mvp.tar.gz" ]; then
    echo "Found archive in home directory, extracting..."
    tar -xzf $HOME/teamflow-mvp.tar.gz -C $PROJECT_DIR --strip-components=1
elif [ -f "./teamflow-mvp.tar.gz" ]; then
    echo "Found archive in current directory, extracting..."
    tar -xzf ./teamflow-mvp.tar.gz --strip-components=1
else
    echo -e "${RED}Error: teamflow-mvp.tar.gz not found${NC}"
    echo "Please upload the archive to $HOME or $PROJECT_DIR"
    exit 1
fi

echo -e "${GREEN}✓ Project extracted${NC}"

# Step 4: Configure environment
echo -e "${YELLOW}[4/6] Configuring environment...${NC}"

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    
    echo ""
    echo -e "${YELLOW}⚠️  Configuration required!${NC}"
    echo ""
    echo "Please provide the following information:"
    echo ""
    
    # Get Telegram Bot Token
    read -p "Telegram Bot Token (from @BotFather): " BOT_TOKEN
    read -p "Telegram Chat ID (numeric): " CHAT_ID
    
    # Update .env file
    sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$BOT_TOKEN/" backend/.env
    sed -i "s/TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=$CHAT_ID/" backend/.env
    
    # Get server IP for CORS
    SERVER_IP=$(curl -s ifconfig.me)
    sed -i "s/BACKEND_CORS_ORIGINS=.*/BACKEND_CORS_ORIGINS=[\"http:\/\/$SERVER_IP:5173\",\"http:\/\/localhost:5173\"]/" backend/.env
    
    echo -e "${GREEN}✓ Environment configured${NC}"
else
    echo -e "${GREEN}✓ Using existing .env file${NC}"
fi

# Step 5: Setup firewall
echo -e "${YELLOW}[5/6] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 5173/tcp
    ufw allow 8000/tcp
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠️  UFW not installed, skipping firewall setup${NC}"
fi

# Step 6: Deploy application
echo -e "${YELLOW}[6/6] Deploying application...${NC}"

# Stop existing containers if any
if docker-compose ps -q 2>/dev/null | grep -q .; then
    echo "Stopping existing containers..."
    docker-compose down
fi

# Use production compose if exists, otherwise use default
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

echo "Building and starting containers..."
docker-compose -f $COMPOSE_FILE up -d --build

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check health
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Application deployed successfully${NC}"
else
    echo -e "${RED}✗ Some services failed to start${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# Setup systemd service for auto-restart
echo -e "${YELLOW}Setting up auto-restart service...${NC}"
cat > /etc/systemd/system/teamflow.service <<EOF
[Unit]
Description=TeamFlow Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose -f $COMPOSE_FILE up -d
ExecStop=/usr/local/bin/docker-compose -f $COMPOSE_FILE down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable teamflow
echo -e "${GREEN}✓ Auto-restart configured${NC}"

# Create backup script
echo -e "${YELLOW}Creating backup script...${NC}"
mkdir -p /opt/teamflow-backups
cat > /opt/teamflow/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/teamflow-backups"
DATE=$(date +%Y%m%d-%H%M)
docker cp teamflow-backend:/app/data/teamflow.db $BACKUP_DIR/teamflow-$DATE.db
# Keep only last 30 days
find $BACKUP_DIR -name "teamflow-*.db" -mtime +30 -delete
echo "Backup created: teamflow-$DATE.db"
EOF

chmod +x /opt/teamflow/backup.sh

# Add to cron
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/teamflow/backup.sh") | crontab -
echo -e "${GREEN}✓ Daily backup configured (02:00)${NC}"

# Final summary
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║   Deployment Complete! ✓              ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

SERVER_IP=$(curl -s ifconfig.me)

echo -e "${BLUE}Access your application:${NC}"
echo ""
echo "  📱 Web UI:    http://$SERVER_IP:5173"
echo "  🔌 API:       http://$SERVER_IP:8000"
echo "  📚 API Docs:  http://$SERVER_IP:8000/docs"
echo ""
echo -e "${BLUE}Telegram Bot:${NC}"
echo "  Test your bot with: /task or /week"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs:    docker-compose logs -f"
echo "  Restart:      docker-compose restart"
echo "  Stop:         docker-compose down"
echo "  Backup:       /opt/teamflow/backup.sh"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open http://$SERVER_IP:5173 in your browser"
echo "  2. Test the bot in Telegram with /task"
echo "  3. Set up a domain and SSL (optional)"
echo ""
echo -e "${GREEN}Happy task managing! 🚀${NC}"
