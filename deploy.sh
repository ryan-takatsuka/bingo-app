#!/bin/bash

# Bingo Card Generator - AWS EC2 Deployment Script
# Deploys to AWS free tier t2.micro instance using Docker + ECR
#
# Prerequisites:
# 1. AWS CLI configured with appropriate permissions
# 2. EC2 instance running Amazon Linux 2 with Docker installed
# 3. ECR repository created
# 4. Security group allowing inbound traffic on port 8080
# 5. SSH access to EC2 instance (or SSM Session Manager)
#
# Usage:
#   ./deploy.sh [options]
#
# Options:
#   --ecr-repo     ECR repository URI (required)
#   --instance-id  EC2 instance ID (required for SSM)
#   --ssh-host     SSH hostname/IP (alternative to SSM)
#   --ssh-key      SSH private key path (required with --ssh-host)
#   --region       AWS region (default: us-west-2)
#   --tag          Docker image tag (default: latest)
#   --help         Show this help

set -e

# Default values
AWS_REGION="us-west-2"
DOCKER_TAG="latest"
APP_NAME="bingo-card-generator"
CONTAINER_NAME="bingo-app"
PORT="8080"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

usage() {
    echo "Usage: $0 --ecr-repo <repo-uri> [--instance-id <id> | --ssh-host <host> --ssh-key <key>] [options]"
    echo ""
    echo "Options:"
    echo "  --ecr-repo <uri>      ECR repository URI (required)"
    echo "  --instance-id <id>    EC2 instance ID for SSM deployment"
    echo "  --ssh-host <host>     SSH hostname/IP (alternative to SSM)"
    echo "  --ssh-key <key>       SSH private key path (required with --ssh-host)"
    echo "  --region <region>     AWS region (default: us-west-2)"
    echo "  --tag <tag>           Docker image tag (default: latest)"
    echo "  --help                Show this help"
    echo ""
    echo "Example (SSM):"
    echo "  $0 --ecr-repo 123456789012.dkr.ecr.us-west-2.amazonaws.com/bingo-app --instance-id i-1234567890abcdef0"
    echo ""
    echo "Example (SSH):"
    echo "  $0 --ecr-repo 123456789012.dkr.ecr.us-west-2.amazonaws.com/bingo-app --ssh-host ec2-user@1.2.3.4 --ssh-key ~/.ssh/my-key.pem"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ecr-repo)
            ECR_REPO="$2"
            shift 2
            ;;
        --instance-id)
            INSTANCE_ID="$2"
            shift 2
            ;;
        --ssh-host)
            SSH_HOST="$2"
            shift 2
            ;;
        --ssh-key)
            SSH_KEY="$2"
            shift 2
            ;;
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --tag)
            DOCKER_TAG="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate required parameters
if [ -z "$ECR_REPO" ]; then
    error "ECR repository URI is required. Use --ecr-repo"
fi

if [ -z "$INSTANCE_ID" ] && [ -z "$SSH_HOST" ]; then
    error "Either --instance-id (for SSM) or --ssh-host (for SSH) is required"
fi

if [ -n "$SSH_HOST" ] && [ -z "$SSH_KEY" ]; then
    error "SSH key is required when using --ssh-host"
fi

if [ -n "$SSH_KEY" ] && [ ! -f "$SSH_KEY" ]; then
    error "SSH key file not found: $SSH_KEY"
fi

# Check if running in project directory
if [ ! -f "app.py" ] || [ ! -f "Dockerfile" ]; then
    error "Please run this script from the project root directory"
fi

# Check if required tools are installed
command -v aws >/dev/null 2>&1 || error "AWS CLI is required but not installed"
command -v docker >/dev/null 2>&1 || error "Docker is required but not installed"

# Full image name
FULL_IMAGE="$ECR_REPO:$DOCKER_TAG"

log "Starting deployment of $APP_NAME"
log "Target image: $FULL_IMAGE"
log "AWS Region: $AWS_REGION"

# Step 1: Build Docker image
log "Building Docker image..."
docker build -t "$APP_NAME:$DOCKER_TAG" .

# Step 2: Tag image for ECR
log "Tagging image for ECR..."
docker tag "$APP_NAME:$DOCKER_TAG" "$FULL_IMAGE"

# Step 3: Login to ECR
log "Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REPO"

# Step 4: Push to ECR
log "Pushing image to ECR..."
docker push "$FULL_IMAGE"

# Step 5: Deploy to EC2
log "Deploying to EC2 instance..."

# Create deployment commands
DEPLOY_COMMANDS="
# Update system and install Docker if needed
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | sudo docker login --username AWS --password-stdin $ECR_REPO

# Stop and remove existing container if it exists
sudo docker stop $CONTAINER_NAME 2>/dev/null || true
sudo docker rm $CONTAINER_NAME 2>/dev/null || true

# Pull latest image
sudo docker pull $FULL_IMAGE

# Run new container
sudo docker run -d \\
    --name $CONTAINER_NAME \\
    --restart unless-stopped \\
    -p $PORT:$PORT \\
    -e PORT=$PORT \\
    -e HOST=0.0.0.0 \\
    -e FLASK_ENV=production \\
    -e FLASK_DEBUG=False \\
    $FULL_IMAGE

# Check if container is running
sleep 5
if sudo docker ps | grep -q $CONTAINER_NAME; then
    echo 'Container is running successfully'
    sudo docker logs --tail 10 $CONTAINER_NAME
else
    echo 'Container failed to start'
    sudo docker logs $CONTAINER_NAME
    exit 1
fi
"

# Execute deployment based on connection method
if [ -n "$INSTANCE_ID" ]; then
    # Deploy via SSM Session Manager
    log "Deploying via SSM Session Manager to instance: $INSTANCE_ID"
    
    # Create temporary script file
    SCRIPT_ID=$(date +%s)
    SCRIPT_FILE="/tmp/deploy-bingo-$SCRIPT_ID.sh"
    
    echo "$DEPLOY_COMMANDS" > "$SCRIPT_FILE"
    
    # Send and execute script via SSM
    aws ssm send-command \
        --instance-ids "$INSTANCE_ID" \
        --document-name "AWS-RunShellScript" \
        --parameters "commands=[\"$(cat $SCRIPT_FILE | sed 's/"/\\"/g')\"]" \
        --region "$AWS_REGION"
        
    rm "$SCRIPT_FILE"
    
elif [ -n "$SSH_HOST" ]; then
    # Deploy via SSH
    log "Deploying via SSH to host: $SSH_HOST"
    
    # Execute commands via SSH
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_HOST" "$DEPLOY_COMMANDS"
    
    # Check deployment status
    log "Checking deployment status..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_HOST" "
        if sudo docker ps | grep -q $CONTAINER_NAME; then
            echo 'Deployment successful! Container is running.'
            echo 'Access your app at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$PORT'
        else
            echo 'Deployment failed. Container is not running.'
            exit 1
        fi
    "
fi

log "Deployment completed successfully!"
log ""
log "Next steps:"
log "1. Verify the app is accessible on port $PORT"
log "2. Configure your domain name or load balancer if needed"
log "3. Set up CloudWatch monitoring and logging"
log "4. Consider setting up automatic deployments with GitHub Actions"
log ""
log "Useful commands:"
log "  Check logs: docker logs $CONTAINER_NAME"
log "  Stop app: docker stop $CONTAINER_NAME"
log "  Restart app: docker restart $CONTAINER_NAME"