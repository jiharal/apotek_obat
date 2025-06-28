# 🚀 Deployment Guide - Apotek Obat Price Extractor

Panduan lengkap untuk mendeploy aplikasi ekstraksi harga obat menggunakan Docker Compose.

## 📋 Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Minimal 2GB RAM
- 1GB storage space

## 🛠️ Quick Start

### 1. Development Mode (Recommended untuk Testing)

```bash
# Clone atau download project
cd apotek_obat

# Build dan jalankan aplikasi
docker-compose up --build

# Akses aplikasi di http://localhost:8501
```

### 2. Production Mode (dengan Nginx)

```bash
# Jalankan dengan Nginx reverse proxy
docker-compose --profile production up --build -d

# Akses aplikasi di http://localhost
```

### 3. Background Mode

```bash
# Jalankan di background
docker-compose up -d --build

# Lihat logs
docker-compose logs -f

# Stop aplikasi
docker-compose down
```

## 📁 File Structure

```
apotek_obat/
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Service orchestration
├── nginx.conf              # Nginx configuration (production)
├── requirements.txt         # Python dependencies
├── .dockerignore           # Files to exclude from build
├── app.py                  # Main Streamlit application
├── utils/                  # Application utilities
├── pbf/                    # PDF upload directory (persistent)
├── data/                   # Additional data storage
└── DEPLOY.md              # This documentation
```

## ⚙️ Configuration

### Environment Variables

Dapat diatur di `docker-compose.yml`:

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - PYTHONUNBUFFERED=1
```

### Volume Mounting

- `./pbf:/app/pbf` - Persistent PDF storage
- `./data:/app/data` - Additional data storage

### Port Configuration

- **Development**: `8501:8501` (direct Streamlit)
- **Production**: `80:80`, `443:443` (through Nginx)

## 🔧 Customization

### 1. Mengubah Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8501"  # Akses via http://localhost:9000
```

### 2. SSL/HTTPS Setup

1. Simpan certificate files di folder `ssl/`:
   ```
   ssl/
   ├── cert.pem
   └── key.pem
   ```

2. Uncomment SSL section di `nginx.conf`

3. Update `docker-compose.yml`:
   ```yaml
   volumes:
     - ./ssl:/etc/nginx/ssl:ro
   ```

### 3. Custom Domain

Edit `nginx.conf`:
```nginx
server_name your-domain.com;
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Check via Nginx (production)
curl http://localhost/health
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f apotek-obat

# View Nginx logs (production)
docker-compose logs -f nginx
```

### Updates

```bash
# Update and rebuild
docker-compose down
docker-compose up --build -d

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 Security Considerations

### 1. File Upload Limits
- Max file size: 50MB (configurable in nginx.conf)
- Allowed types: PDF only

### 2. Rate Limiting
- 10 requests per second per IP
- Burst: 20 requests

### 3. Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection enabled

### 4. Network Security
- Application runs in isolated Docker network
- Only necessary ports exposed

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Check what's using the port
   lsof -i :8501
   
   # Use different port
   # Edit docker-compose.yml ports section
   ```

2. **Permission issues with volumes**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER pbf/ data/
   ```

3. **Build failures**:
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose build --no-cache
   ```

4. **Memory issues**:
   ```bash
   # Increase Docker memory limit
   # Or use lighter Python image in Dockerfile
   ```

### Performance Tuning

1. **For large PDF files**:
   - Increase memory limits in docker-compose.yml
   - Adjust nginx client_max_body_size

2. **For high traffic**:
   - Scale application containers
   - Use external load balancer
   - Add Redis for session management

## 📈 Production Deployment

### 1. Cloud Deployment (AWS/GCP/Azure)

```bash
# Use cloud-specific docker-compose overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. Container Registry

```bash
# Build and tag
docker build -t your-registry/apotek-obat:latest .

# Push to registry
docker push your-registry/apotek-obat:latest
```

### 3. Backup Strategy

```bash
# Backup persistent data
tar -czf backup-$(date +%Y%m%d).tar.gz pbf/ data/

# Restore
tar -xzf backup-YYYYMMDD.tar.gz
```

## 🆘 Support

### Logs to Check
1. Application logs: `docker-compose logs apotek-obat`
2. Nginx logs: `docker-compose logs nginx`
3. System resources: `docker stats`

### Common Debugging Commands
```bash
# Enter running container
docker-compose exec apotek-obat /bin/bash

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart apotek-obat
```

---

## 📝 Notes

- Aplikasi akan otomatis restart jika container crash
- Data PDF tersimpan persistent di folder `pbf/`
- Health check berjalan setiap 30 detik
- Cocok untuk deployment production dengan Nginx