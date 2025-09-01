# ML Pipeline Monitoring System

This monitoring system provides comprehensive observability for your Mathematics Score Prediction ML pipeline using Prometheus, Grafana, and AlertManager.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ML Pipeline   │───▶│   Prometheus    │───▶│    Grafana      │
│   (Your App)    │    │   (Metrics)     │    │ (Visualization) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Metrics Server  │    │  AlertManager   │
│  (Port 8001)    │    │   (Alerts)      │
└─────────────────┘    └─────────────────┘
```

## 📁 Files Overview

- **`prometheus.yml`**: Prometheus configuration for scraping metrics
- **`alert_rules.yml`**: Alert rules for ML pipeline monitoring
- **`alertmanager.yml`**: AlertManager configuration for notifications
- **`docker-compose.yml`**: Docker setup for the entire monitoring stack
- **`ml_metrics_server.py`**: Python server to expose ML pipeline metrics

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for metrics server)
- Your ML pipeline artifacts in `../artifacts/` directory

### 2. Start the Monitoring Stack
```bash
# Navigate to monitoring directory
cd monitoring

# Start all monitoring services
docker-compose up -d

# Check if services are running
docker-compose ps
```

### 3. Start the ML Metrics Server
```bash
# Install Flask if not already installed
pip install flask

# Start the metrics server
python ml_metrics_server.py
```

### 4. Access the Monitoring Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **AlertManager** | http://localhost:9093 | - |
| **Metrics Endpoint** | http://localhost:8001/metrics | - |

## 📊 Monitored Metrics

### Model Performance
- `ml_model_r2_score`: Model R² accuracy score
- `ml_model_rmse`: Root Mean Square Error
- `ml_model_mae`: Mean Absolute Error

### Pipeline Health
- `ml_pipeline_success`: Overall pipeline success (0/1)
- `ml_pipeline_duration_seconds`: Pipeline execution time
- `ml_data_ingestion_success`: Data ingestion status (0/1)
- `ml_data_validation_success`: Data validation status (0/1)

### System Resources
- CPU usage, Memory usage, Disk space
- Network I/O, System load

## 🚨 Alert Rules

### Critical Alerts
- **ModelAccuracyCritical**: R² score < 0.7
- **DataIngestionFailure**: Data ingestion fails
- **PipelineFailure**: Overall pipeline failure

### Warning Alerts
- **ModelAccuracyDrop**: R² score < 0.8
- **DataValidationFailure**: Data validation issues
- **PipelineExecutionTime**: Execution time > 5 minutes
- **HighMemoryUsage**: Memory usage > 90%
- **HighCPUUsage**: CPU usage > 80%

## 🔧 Configuration

### Email Notifications
Edit `alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'your-smtp-server:587'
  smtp_from: 'ml-pipeline@yourcompany.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
```

### Slack Notifications
Add your Slack webhook URL in `alertmanager.yml`:
```yaml
slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#ml-alerts'
```

## 🔄 Integration with ML Pipeline

### Option 1: Manual Integration
Run the metrics server alongside your pipeline:
```bash
# Terminal 1: Run your ML pipeline
python main.py

# Terminal 2: Run metrics server
python monitoring/ml_metrics_server.py
```

### Option 2: Automated Integration
Add to your `main.py`:
```python
import subprocess
import threading

def start_metrics_server():
    subprocess.run(['python', 'monitoring/ml_metrics_server.py'])

# Start metrics server in background
metrics_thread = threading.Thread(target=start_metrics_server)
metrics_thread.daemon = True
metrics_thread.start()

# Your existing pipeline code
# ... rest of your main.py
```

## 📈 Creating Grafana Dashboards

1. Access Grafana at http://localhost:3000
2. Login with admin/admin123
3. Add Prometheus as data source: http://prometheus:9090
4. Create dashboards with these queries:

**Model Performance Panel:**
```promql
ml_model_r2_score
ml_model_rmse
ml_model_mae
```

**Pipeline Health Panel:**
```promql
ml_pipeline_success
ml_data_ingestion_success
ml_data_validation_success
```

## 🛠️ Troubleshooting

### Common Issues

1. **Metrics not appearing**
   - Check if ml_metrics_server.py is running
   - Verify artifacts directory exists
   - Check Prometheus targets at http://localhost:9090/targets

2. **Alerts not firing**
   - Verify alert rules syntax in Prometheus UI
   - Check AlertManager configuration
   - Ensure email/Slack credentials are correct

3. **Docker services not starting**
   - Check Docker logs: `docker-compose logs [service-name]`
   - Verify port availability
   - Check file permissions

### Useful Commands
```bash
# View logs
docker-compose logs prometheus
docker-compose logs alertmanager
docker-compose logs grafana

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Remove all data (reset)
docker-compose down -v
```

## 🔄 Maintenance

### Regular Tasks
- Monitor disk usage for metrics storage
- Update alert thresholds based on model performance
- Review and tune alert rules
- Backup Grafana dashboards
- Update Docker images regularly

### Scaling
- For production: Use external databases for Grafana
- Consider Prometheus federation for multiple environments
- Implement proper authentication and SSL certificates

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker logs
3. Verify configuration files
4. Check Prometheus/Grafana documentation

---

# 🚀 Production Deployment on Vercel

## Two-Deployment Strategy

### **Deployment 1: ML Model API**
**Purpose**: User-facing prediction API
**URL**: `https://your-ml-api.vercel.app`

### **Deployment 2: Monitoring Dashboard**
**Purpose**: Live monitoring and metrics
**URL**: `https://your-monitoring.vercel.app`

## 📋 Deployment Steps

### **Step 1: Deploy ML Model API**

1. **Prepare your repository**:
   ```bash
   # Copy your trained model files
   cp -r artifacts/ ./
   cp requirements-vercel.txt requirements.txt
   ```

2. **Deploy to Vercel**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Deploy
   vercel --prod
   ```

3. **Configure environment**:
   - Set `PYTHONPATH=.` in Vercel dashboard
   - Upload model files to deployment

### **Step 2: Deploy Monitoring Dashboard**

1. **Create separate repository** for monitoring:
   ```bash
   mkdir ml-monitoring
   cd ml-monitoring
   cp monitoring/vercel-monitoring.py ./
   cp monitoring/vercel.json ./
   cp monitoring/requirements.txt ./
   ```

2. **Update configuration**:
   - Edit `vercel.json` to set `MAIN_API_URL` to your ML API URL

3. **Deploy monitoring**:
   ```bash
   vercel --prod
   ```

## 🔧 Production Configuration

### **Environment Variables**

**ML API Deployment**:
- `PYTHONPATH=.`
- `MODEL_VERSION=1.0`

**Monitoring Deployment**:
- `MAIN_API_URL=https://your-ml-api.vercel.app`
- `MONITORING_REFRESH_RATE=30`

### **API Endpoints**

**ML API** (`https://your-ml-api.vercel.app`):
- `POST /api/predict` - Make predictions
- `GET /api/health` - Health check
- `GET /api/model-info` - Model metrics
- `GET /` - User interface

**Monitoring** (`https://your-monitoring.vercel.app`):
- `GET /` - Monitoring dashboard
- `GET /api/status` - API status
- `GET /api/metrics` - Prometheus metrics
- `GET /api/dashboard` - HTML dashboard

## 📊 Production Features

### **ML API Features**:
- ✅ Real-time predictions
- ✅ Input validation
- ✅ Error handling
- ✅ Health monitoring
- ✅ User-friendly interface
- ✅ Prediction logging

### **Monitoring Features**:
- ✅ Live API health monitoring
- ✅ Model performance tracking
- ✅ Response time monitoring
- ✅ Beautiful dashboard
- ✅ Auto-refresh every 30 seconds
- ✅ Prometheus metrics export

## 🔒 Security Considerations

1. **Rate Limiting**: Add rate limiting to prevent abuse
2. **Input Validation**: Validate all inputs thoroughly
3. **Error Handling**: Don't expose internal errors
4. **Monitoring**: Monitor for unusual patterns
5. **HTTPS**: Always use HTTPS in production

## 📈 Scaling Considerations

1. **Serverless**: Vercel automatically scales
2. **Cold Starts**: First request may be slower
3. **Memory Limits**: Optimize model size
4. **Timeout**: 30-second function timeout
5. **Monitoring**: Use external monitoring for 24/7 uptime

## 🎯 Benefits of This Architecture

1. **Separation of Concerns**: API and monitoring are separate
2. **Independent Scaling**: Each service scales independently
3. **High Availability**: If one fails, the other continues
4. **Easy Updates**: Deploy updates without affecting monitoring
5. **Cost Effective**: Pay only for what you use
6. **Global CDN**: Fast response times worldwide
