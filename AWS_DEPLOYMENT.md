# 🚀 AWS EC2 Deployment Guide for AI Text Spotter

Deploy AI Text Spotter to AWS EC2 t3.micro (Free Tier) with Docker.

---

## Prerequisites

- AWS account with Free Tier
- AWS CLI configured locally
- SSH key: `sentiment-analysis-key.pem` (already in ~/.ssh/)
- Basic AWS knowledge (EC2, Security Groups)

---

## Step 1: Launch EC2 Instance

### Instance Configuration

1. **Go to EC2 Dashboard** → Launch Instance

2. **Choose settings:**
   - **Name**: `ai-text-spotter-production`
   - **AMI**: Ubuntu Server 24.04 LTS (Free Tier eligible)
   - **Instance Type**: `t3.micro` (1 vCPU, 1GB RAM)
   - **Key pair**: `sentiment-analysis-key` (existing)
   - **Storage**: 15GB gp3 (default)

3. **Network Settings** - Configure Security Group:

```
Inbound Rules:
┌──────────┬────────┬────────────┬─────────────────────────────────┐
│ Type     │ Port   │ Source     │ Description                     │
├──────────┼────────┼────────────┼─────────────────────────────────┤
│ SSH      │ 22     │ My IP      │ SSH access (your IP only)       │
│ HTTP     │ 80     │ 0.0.0.0/0  │ Frontend public access          │
│ Custom   │ 8000   │ 0.0.0.0/0  │ Backend API (optional: restrict)│
└──────────┴────────┴────────────┴─────────────────────────────────┘

Outbound Rules:
- All traffic → 0.0.0.0/0 (default)
```

⚠️ **Security Note**: For production, restrict port 8000 to frontend IP only.

4. **Launch Instance**

---

## Step 2: Allocate Elastic IP (Permanent Address)

Elastic IP ensures your instance keeps the same public IP after restarts.

```bash
# In AWS Console:
1. EC2 → Elastic IPs → "Allocate Elastic IP address"
2. Select new IP → Actions → "Associate Elastic IP address"
3. Choose your instance: ai-text-spotter-production
4. Note the IP address (e.g., 13.48.16.109)
```

**Benefits:**
- ✅ Permanent IP (survives instance stop/start)
- ✅ Free while associated with running instance
- ✅ Can point custom domain to it

---

## Step 3: Connect to Instance

```bash
# Replace with your Elastic IP
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@YOUR_ELASTIC_IP

# Example:
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@13.48.16.109
```

---

## Step 4: Setup 4GB Swap Memory (CRITICAL)

**Why needed:**
- Docker build requires ~2GB memory (peaks during backend build)
- Model loading (sentence-transformers + torch) needs ~800MB
- Total: Need 2.8GB, but we only have 1GB RAM → 4GB swap ensures safety

```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify swap is active
free -h
# Should show:
#               total        used        free      shared  buff/cache   available
# Mem:           951Mi       180Mi       600Mi       1.0Mi       170Mi       620Mi
# Swap:          4.0Gi          0B       4.0Gi

# Make swap permanent (survives reboots)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize swap usage (use swap only when really needed)
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## Step 5: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group (no need for sudo docker)
sudo usermod -aG docker ubuntu

# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# IMPORTANT: Log out and back in for group changes to take effect
exit

# SSH back in
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@YOUR_ELASTIC_IP

# Verify Docker works without sudo
docker --version
# Docker version 27.x.x

docker compose version
# Docker Compose version v2.x.x
```

---

## Step 6: Clone Repository

```bash
# Install Git (if not installed)
sudo apt install -y git

# Clone AI Text Spotter repository
git clone https://github.com/YOUR_USERNAME/ai-text-spotter.git
cd ai-text-spotter

# Verify files
ls -la
# Should see: docker-compose.yml, backend/, frontend/, nginx.conf
```

---

## Step 7: Configure Environment

```bash
# Create .env file (if using GROQ API for jury detector - optional)
nano .env
```

Paste this content (optional - only if you want to keep GROQ jury detector):
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
MAX_TEXT_LENGTH=10000
MAX_FILE_SIZE_MB=5
BATCH_SIZE=10
ENABLE_CACHING=true
```

**Note:** Since we replaced the ensemble with semantic embedding detector, GROQ API key is optional.

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 8: Build and Deploy

**Note:** Initial build takes ~10-15 minutes on t3.micro due to:
- Backend: ~2GB image (PyTorch CPU, sentence-transformers, dependencies)
- Frontend: 20MB image (nginx + static files)

```bash
# Build and start containers
docker compose up -d --build

# Monitor build progress (optional)
docker compose logs -f backend

# Wait for completion - you'll see:
# ✔ Container ai-text-spotter-backend   Started
# ✔ Container ai-text-spotter-frontend  Started
```

**Expected build time:**
- Backend: ~10-12 minutes (downloading PyTorch CPU, sentence-transformers)
- Frontend: ~30 seconds
- Total: ~12-15 minutes

---

## Step 9: Verify Deployment

```bash
# Check containers are running
docker compose ps
# Should show both containers as "Up" and "healthy"

# Check backend health
curl http://localhost:8000/api/health | python3 -m json.tool
# Should return:
# {
#   "status": "healthy",
#   "models_loaded": {
#     "semantic_embedding": true
#   }
# }

# Check frontend
curl http://localhost
# Should return HTML content
```

---

## Step 10: Access Your Application

Open your browser:

**Frontend:** `http://YOUR_ELASTIC_IP`
- Example: http://13.48.16.109

**Backend API:** `http://YOUR_ELASTIC_IP:8000`
- Health: http://13.48.16.109:8000/api/health
- Docs: http://13.48.16.109:8000/docs

---

## Management Commands

```bash
# View logs
docker compose logs -f                 # All containers
docker compose logs -f backend        # Backend only
docker compose logs -f frontend       # Frontend only

# Restart services
docker compose restart

# Stop services
docker compose stop

# Start services
docker compose start

# Rebuild after code changes
git pull origin main
docker compose down
docker compose up -d --build

# Check disk usage
df -h
docker system df

# Clean up unused images/containers (frees space)
docker system prune -f
```

---

## Monitoring & Troubleshooting

### Memory Usage

```bash
# Check system memory
free -h

# Check Docker container memory
docker stats

# If backend crashes with OOM:
# 1. Increase swap to 8GB:
sudo swapoff /swapfile
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Container Issues

```bash
# If backend is unhealthy:
docker logs ai-text-spotter-backend --tail 100

# Common issues:
# - Model download timeout → wait longer (sentence-transformers downloads ~90MB)
# - OOM error → increase swap
# - Port already in use → docker compose down && docker compose up -d

# If frontend shows 502 Bad Gateway:
# - Backend not ready yet (wait 2-3 minutes after start)
# - Check backend health: curl http://localhost:8000/api/health
```

### Performance Tips

```bash
# Reduce memory usage in docker-compose.yml:
# backend:
#   mem_limit: 800m  # Instead of 900m

# Monitor first model load (takes ~25 seconds):
docker compose logs -f backend | grep "Loading semantic embedding model"
```

---

## Security Hardening (Production)

```bash
# 1. Restrict SSH to your IP only in Security Group
# 2. Close port 8000 (backend) to public, only allow from nginx

# 3. Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw enable

# 4. Setup HTTPS with Let's Encrypt (optional)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Cost Optimization

**Free Tier Usage (12 months):**
- ✅ t3.micro: 750 hours/month (1 instance 24/7)
- ✅ 15GB EBS storage
- ✅ Elastic IP (free while associated)
- ✅ 100GB outbound data/month

**After Free Tier (~$7-9/month):**
- t3.micro: ~$7.50/month
- 15GB EBS: ~$1.50/month
- Data transfer: ~$0-1/month

**Reduce costs:**
- Stop instance when not in use (Elastic IP stays free)
- Use t3.micro only (don't upgrade unless needed)
- Monitor CloudWatch for usage

---

## Updating the Application

```bash
# 1. SSH to instance
ssh -i ~/.ssh/sentiment-analysis-key.pem ubuntu@YOUR_ELASTIC_IP

# 2. Navigate to project
cd ai-text-spotter

# 3. Pull latest changes
git pull origin main

# 4. Rebuild and restart
docker compose down
docker compose up -d --build

# 5. Verify
curl http://localhost:8000/api/health
```

---

## Backup & Recovery

```bash
# Backup configuration
cp .env .env.backup

# Backup models (if custom embeddings)
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Download backup to local machine
scp -i ~/.ssh/sentiment-analysis-key.pem ubuntu@YOUR_ELASTIC_IP:~/ai-text-spotter/models_backup*.tar.gz ~/backups/
```

---

## Next Steps

1. ✅ **Test all features** - upload text, analyze, check results
2. 🌐 **Setup custom domain** (optional):
   - Point A record to Elastic IP
   - Setup nginx SSL
   - Add Let's Encrypt certificate
3. 📊 **Monitor performance**:
   - CloudWatch metrics
   - Docker stats
   - Application logs
4. 🔒 **Enhance security**:
   - Restrict port 8000 to localhost only
   - Setup HTTPS
   - Enable AWS CloudWatch alarms

---

## Support

- **GitHub**: https://github.com/YOUR_USERNAME/ai-text-spotter
- **Issues**: Report bugs via GitHub Issues

---

**Deployed Successfully! 🎉**

Your AI Text Spotter is now live at: `http://YOUR_ELASTIC_IP`

Model specifications:
- **Semantic Embedding**: all-MiniLM-L6-v2 (384-dimensional)
- **Detection Method**: STD-based classification (92.7% accuracy)
- **First request**: ~25 seconds (model loading)
- **Subsequent requests**: 200-500ms
