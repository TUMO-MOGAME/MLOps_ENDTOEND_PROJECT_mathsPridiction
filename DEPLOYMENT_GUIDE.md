# 🚀 Vercel Deployment Guide

## Two-Deployment Architecture

### **Deployment 1: ML Model API** 
- **Purpose**: User-facing prediction API
- **Files**: `api/predict.py`, `vercel.json`, `static/index.html`
- **URL**: `https://your-ml-api.vercel.app`

### **Deployment 2: Monitoring Dashboard**
- **Purpose**: Live monitoring and metrics
- **Files**: `monitoring/vercel-monitoring.py`, `monitoring/vercel.json`
- **URL**: `https://your-monitoring.vercel.app`

---

## 📋 Step-by-Step Deployment

### **Step 1: Prepare ML Model API**

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Prepare files**:
   ```bash
   # Ensure you have these files:
   # - api/predict.py (✅ Created)
   # - vercel.json (✅ Fixed - removed functions property)
   # - static/index.html (✅ Created)
   # - requirements-vercel.txt (✅ Created)
   # - artifacts/ folder with your trained model
   ```

3. **Copy requirements**:
   ```bash
   cp requirements-vercel.txt requirements.txt
   ```

4. **Deploy ML API**:
   ```bash
   # Initialize Vercel project
   vercel

   # Deploy to production
   vercel --prod
   ```

### **⚠️ Important Fix Applied:**
The original `vercel.json` had both `builds` and `functions` properties, which caused deployment errors. This has been fixed by:
- Removing the `functions` property
- Using modern `rewrites` instead of `routes`
- Simplified configuration for better compatibility

### **Step 2: Deploy Monitoring Dashboard**

1. **Create monitoring repository**:
   ```bash
   mkdir ml-monitoring-deploy
   cd ml-monitoring-deploy
   
   # Copy monitoring files
   cp ../monitoring/vercel-monitoring.py ./
   cp ../monitoring/vercel.json ./
   cp ../monitoring/requirements.txt ./
   ```

2. **Update monitoring config**:
   - Edit `vercel.json` and replace `"https://your-ml-api.vercel.app"` with your actual ML API URL

3. **Deploy monitoring**:
   ```bash
   vercel --prod
   ```

---

## 🔧 Configuration

### **Environment Variables (Set in Vercel Dashboard)**

**ML API Project**:
- `PYTHONPATH` = `.`
- `MODEL_VERSION` = `1.0`

**Monitoring Project**:
- `MAIN_API_URL` = `https://your-actual-ml-api.vercel.app`

---

## 🌐 API Endpoints

### **ML API Endpoints**:
- `GET /` - User interface for predictions
- `POST /api/predict` - Make predictions
- `GET /api/health` - Health check
- `GET /api/model-info` - Model performance metrics

### **Monitoring Endpoints**:
- `GET /` - Live monitoring dashboard
- `GET /api/status` - Simple status JSON
- `GET /api/metrics` - Prometheus metrics
- `GET /api/dashboard` - HTML dashboard

---

## 📊 Features

### **User-Facing Features**:
✅ Beautiful web interface for predictions  
✅ Real-time mathematics score predictions  
✅ Input validation and error handling  
✅ Mobile-responsive design  

### **Monitoring Features**:
✅ Live API health monitoring  
✅ Model performance tracking (88% accuracy)  
✅ Response time monitoring  
✅ Auto-refreshing dashboard  
✅ Prometheus metrics export  

---

## 🎯 Production Benefits

1. **Serverless**: Automatic scaling, no server management
2. **Global CDN**: Fast response times worldwide
3. **High Availability**: 99.9% uptime SLA
4. **Cost Effective**: Pay only for requests
5. **Easy Updates**: Deploy with `vercel --prod`
6. **Monitoring**: Separate monitoring ensures reliability

---

## 🔍 Testing Your Deployment

### **Test ML API**:
```bash
# Health check
curl https://your-ml-api.vercel.app/api/health

# Test prediction
curl -X POST https://your-ml-api.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "race_ethnicity": "group C",
    "parental_level_of_education": "bachelor'\''s degree",
    "lunch": "standard",
    "test_preparation_course": "completed",
    "reading_score": 75,
    "writing_score": 80
  }'
```

### **Test Monitoring**:
```bash
# Status check
curl https://your-monitoring.vercel.app/api/status

# Metrics
curl https://your-monitoring.vercel.app/api/metrics
```

---

## 🚨 Important Notes

1. **Model Files**: Make sure your `artifacts/` folder is included in deployment
2. **Dependencies**: Use `requirements-vercel.txt` for production dependencies
3. **Timeouts**: Vercel has 30-second function timeout
4. **Memory**: Optimize model size for serverless deployment
5. **URLs**: Update monitoring config with actual API URL after first deployment

---

## 🎉 You're Ready!

After deployment, you'll have:
- **User Interface**: Beautiful web app for predictions
- **API**: RESTful API for integrations
- **Monitoring**: Live dashboard showing model performance
- **Metrics**: Prometheus-compatible metrics endpoint
- **Global Scale**: Worldwide availability with CDN

Your ML pipeline is now production-ready! 🚀
