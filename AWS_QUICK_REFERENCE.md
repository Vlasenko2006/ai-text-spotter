# 🚀 Quick Reference Guide - AWS Instance Management

## 1. Restart Containers on Existing Instance

### sentiment-analysis instance (13.48.16.109)
```bash
# SSH into instance
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@13.48.16.109

# Start Docker daemon
sudo systemctl start docker

# Navigate to project and start containers
cd ~/sentiment-analysis-vector-search
sudo docker compose up -d

# Check status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

**One-line command from your local machine:**
```bash
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@13.48.16.109 'sudo systemctl start docker && cd ~/sentiment-analysis-vector-search && sudo docker compose up -d && sudo docker compose ps'
```

---

## 2. Deploy AI Text Spotter to New Instance

### Option A: Use MusicLab Instance (Recommended - Save Costs)

**Instance:** `i-0ed8087de322eeff4` (musiclab-production, currently stopped)

```bash
# 1. Start the instance
aws ec2 start-instances --instance-ids i-0ed8087de322eeff4

# 2. Wait 30 seconds for boot
sleep 30

# 3. Get public IP (temporary - changes on each start)
INSTANCE_IP=$(aws ec2 describe-instances --instance-ids i-0ed8087de322eeff4 \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "Instance IP: $INSTANCE_IP"

# 4. Add SSH access for your current IP
YOUR_IP=$(curl -s https://checkip.amazonaws.com)
SECURITY_GROUP=$(aws ec2 describe-instances --instance-ids i-0ed8087de322eeff4 \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP \
    --protocol tcp --port 22 --cidr $YOUR_IP/32 2>/dev/null || echo "SSH rule already exists"

# 5. Connect and deploy
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@$INSTANCE_IP << 'ENDSSH'
    # Start Docker
    sudo systemctl start docker
    
    # Clone ai-text-spotter
    cd ~
    git clone https://github.com/YOUR_USERNAME/ai-text-spotter.git
    cd ai-text-spotter
    
    # Build and start
    sudo docker compose up -d --build
    
    # Check status
    sudo docker compose ps
ENDSSH

# 6. Access your app
echo "Frontend: http://$INSTANCE_IP"
echo "Backend API: http://$INSTANCE_IP:8000"
```

**Ports used by ai-text-spotter:**
- Frontend: 80
- Backend: 8000

**Access URLs:**
- `http://$INSTANCE_IP` - Frontend
- `http://$INSTANCE_IP:8000/api/health` - Backend health check
- `http://$INSTANCE_IP:8000/docs` - API documentation

---

### Option B: Create New Instance with Temporary IP

**Launch new t3.micro instance:**

```bash
# 1. Create instance (AWS Console recommended)
# - Name: ai-text-spotter-production
# - Instance Type: t3.micro
# - AMI: Ubuntu 24.04 LTS
# - Key Pair: sentiment-analysis-key
# - Security Group: Allow SSH (22), HTTP (80), Custom TCP (8000)

# 2. OR use CLI to launch
aws ec2 run-instances \
    --image-id ami-0014ce3e52359afbd \
    --instance-type t3.micro \
    --key-name sentiment-analysis-key \
    --security-group-ids sg-0f4b0fa36b0c7c3e3 \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ai-text-spotter-production}]' \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":15,"VolumeType":"gp3"}}]' \
    --query 'Instances[0].InstanceId' \
    --output text

# 3. Get the instance ID and IP
INSTANCE_ID="i-XXXXXXXXXXXXXXXXX"  # Replace with actual ID
INSTANCE_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "New Instance IP: $INSTANCE_IP"
echo "This is TEMPORARY - changes every time instance restarts!"
```

---

## 3. Allocate Elastic IP (Permanent Address)

**To get a permanent IP that doesn't change:**

```bash
# 1. Allocate Elastic IP
ALLOCATION_ID=$(aws ec2 allocate-address --domain vpc \
    --query 'AllocationId' --output text)

# 2. Associate with instance
aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID

# 3. Get the permanent IP
ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --query 'Addresses[0].PublicIp' --output text)

echo "Permanent Elastic IP: $ELASTIC_IP"
echo "This IP will NOT change even after instance restarts"
```

**Note:** Elastic IP is FREE while associated with a running instance, but costs $0.005/hour when NOT associated!

---

## 4. Complete Deployment Script

Save as `deploy_ai_text_spotter.sh`:

```bash
#!/bin/bash
# Deploy AI Text Spotter to AWS

INSTANCE_ID="i-0ed8087de322eeff4"  # MusicLab instance
SSH_KEY="$HOME/.ssh/sentiment-analysis-key.pem"

echo "🚀 Deploying AI Text Spotter..."

# Start instance
echo "1. Starting instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID
sleep 30

# Get IP
echo "2. Getting instance IP..."
INSTANCE_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "   IP: $INSTANCE_IP"

# Add SSH access
echo "3. Adding SSH access..."
YOUR_IP=$(curl -s https://checkip.amazonaws.com)
SECURITY_GROUP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP \
    --protocol tcp --port 22 --cidr $YOUR_IP/32 2>/dev/null

# Setup swap and deploy
echo "4. Deploying application..."
ssh -i "$SSH_KEY" ubuntu@$INSTANCE_IP << 'ENDSSH'
    # Setup 4GB swap if not exists
    if [ ! -f /swapfile ]; then
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        sudo sysctl vm.swappiness=10
        echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    fi
    
    # Start Docker
    sudo systemctl start docker
    
    # Clone or update repo
    if [ -d "ai-text-spotter" ]; then
        cd ai-text-spotter && git pull
    else
        git clone https://github.com/YOUR_USERNAME/ai-text-spotter.git
        cd ai-text-spotter
    fi
    
    # Deploy
    sudo docker compose up -d --build
    
    # Show status
    echo ""
    echo "Container status:"
    sudo docker compose ps
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$INSTANCE_IP"
echo "   Backend:  http://$INSTANCE_IP:8000"
echo "   API Docs: http://$INSTANCE_IP:8000/docs"
echo ""
echo "⚠️  This is a TEMPORARY IP - changes on restart!"
echo "   To get permanent IP, allocate Elastic IP in AWS Console"
```

**Make executable and run:**
```bash
chmod +x deploy_ai_text_spotter.sh
./deploy_ai_text_spotter.sh
```

---

## 5. Quick Commands

### Check all your instances
```bash
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,Tags[?Key==`Name`].Value|[0],PublicIpAddress]' \
    --output table
```

### Start any stopped instance
```bash
aws ec2 start-instances --instance-ids i-XXXXXXXXXXXXXXXXX
```

### Stop instance (save costs)
```bash
aws ec2 stop-instances --instance-ids i-XXXXXXXXXXXXXXXXX
```

### Get current public IP of running instance
```bash
aws ec2 describe-instances --instance-ids i-XXXXXXXXXXXXXXXXX \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

---

## 6. Cost Management

**AWS Free Tier (12 months):**
- ✅ 750 hours/month of t3.micro (ONE instance 24/7)
- ✅ 15GB EBS storage per instance
- ✅ Elastic IP is FREE while associated with running instance

**Running 2 instances:**
- Sentiment-analysis: Uses ~400 hours/month (if running 24/7)
- AI Text Spotter: Uses ~400 hours/month
- **Total: 800 hours/month = Exceeds Free Tier by 50 hours = ~$3.75/month**

**Recommendation:**
- Keep ONE instance running 24/7 (Free Tier)
- Start/stop the other as needed
- OR run both on same instance (different ports)

---

## 7. Running Both Apps on One Instance

**Deploy both on same t3.micro (Recommended):**

**Modify ai-text-spotter ports in docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Changed from 8000:8000
  
  frontend:
    ports:
      - "81:80"  # Changed from 80:80
```

**Then access:**
- Sentiment Analysis: http://$IP:3001
- AI Text Spotter Frontend: http://$IP:81
- AI Text Spotter Backend: http://$IP:8080

**Memory check:**
- Sentiment app: ~600MB
- AI Text Spotter: ~471MB
- **Total: ~1GB + 4GB swap = Fits on t3.micro! ✅**

---

**Need help?** Run `./deploy_ai_text_spotter.sh` to deploy automatically!
