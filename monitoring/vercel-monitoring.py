"""
Vercel-compatible monitoring dashboard
This will be deployed as a separate monitoring service
"""

from flask import Flask, jsonify, render_template_string
import json
import os
import requests
from datetime import datetime
import time

app = Flask(__name__)

# Configuration for production monitoring
MAIN_API_URL = os.environ.get('MAIN_API_URL', 'https://your-ml-api.vercel.app')
MONITORING_DATA_URL = os.environ.get('MONITORING_DATA_URL', '')

def get_production_metrics():
    """Get metrics from production API"""
    metrics = {
        'ml_model_r2_score': 0.0,
        'ml_model_rmse': 0.0,
        'ml_model_mae': 0.0,
        'api_health': 0,
        'last_prediction_time': 0,
        'total_predictions': 0,
        'api_response_time': 0
    }
    
    try:
        # Check API health
        health_response = requests.get(f"{MAIN_API_URL}/api/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            metrics['api_health'] = 1 if health_data.get('status') == 'healthy' else 0
        
        # Get model info
        info_response = requests.get(f"{MAIN_API_URL}/api/model-info", timeout=10)
        if info_response.status_code == 200:
            info_data = info_response.json()
            model_metrics = info_data.get('model_metrics', {})
            metrics['ml_model_r2_score'] = model_metrics.get('test_r2', 0.0)
            metrics['ml_model_rmse'] = model_metrics.get('test_rmse', 0.0)
            metrics['ml_model_mae'] = model_metrics.get('test_mae', 0.0)
        
        # Test API response time
        start_time = time.time()
        test_response = requests.get(f"{MAIN_API_URL}/api/health", timeout=10)
        metrics['api_response_time'] = (time.time() - start_time) * 1000  # ms
        
    except Exception as e:
        print(f"Error getting production metrics: {e}")
        metrics['api_health'] = 0
    
    return metrics

@app.route('/api/metrics')
def metrics():
    """Prometheus-style metrics for production"""
    metrics_data = get_production_metrics()
    
    prometheus_metrics = []
    for key, value in metrics_data.items():
        prometheus_metrics.append(f"# HELP {key} Production ML API metric")
        prometheus_metrics.append(f"# TYPE {key} gauge")
        prometheus_metrics.append(f"{key} {value}")
    
    return '\n'.join(prometheus_metrics), 200, {'Content-Type': 'text/plain'}

@app.route('/api/status')
def status():
    """Simple status endpoint for production monitoring"""
    metrics_data = get_production_metrics()
    
    return jsonify({
        'api_status': 'HEALTHY' if metrics_data['api_health'] == 1 else 'UNHEALTHY',
        'model_accuracy': f"{metrics_data['ml_model_r2_score']*100:.2f}%",
        'model_r2_score': round(metrics_data['ml_model_r2_score'], 4),
        'model_rmse': round(metrics_data['ml_model_rmse'], 4),
        'model_mae': round(metrics_data['ml_model_mae'], 4),
        'api_response_time_ms': round(metrics_data['api_response_time'], 2),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'main_api_url': MAIN_API_URL
    })

@app.route('/api/dashboard')
def dashboard():
    """Production monitoring dashboard"""
    metrics_data = get_production_metrics()
    
    # Determine status
    r2_score = metrics_data['ml_model_r2_score']
    if r2_score >= 0.8:
        model_status = "🟢 EXCELLENT"
        status_class = "status-good"
    elif r2_score >= 0.7:
        model_status = "🟡 GOOD"
        status_class = "status-warning"
    else:
        model_status = "🔴 POOR"
        status_class = "status-error"
    
    api_status = "🟢 ONLINE" if metrics_data['api_health'] == 1 else "🔴 OFFLINE"
    api_status_class = "status-good" if metrics_data['api_health'] == 1 else "status-error"
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML API Production Monitoring</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 40px; color: white; }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .metric-card {{ background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }}
            .metric-title {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333; display: flex; align-items: center; }}
            .metric-value {{ font-size: 28px; font-weight: bold; margin: 15px 0; }}
            .status-good {{ color: #28a745; }}
            .status-warning {{ color: #ffc107; }}
            .status-error {{ color: #dc3545; }}
            .timestamp {{ color: #666; font-size: 14px; text-align: center; margin-top: 30px; }}
            .progress-bar {{ width: 100%; height: 25px; background-color: #e9ecef; border-radius: 12px; overflow: hidden; margin: 10px 0; }}
            .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }}
            .metric-detail {{ margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 8px; }}
            .api-link {{ color: #007bff; text-decoration: none; font-weight: bold; }}
            .api-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 ML API Production Monitor</h1>
                <p>Mathematics Score Prediction API - Live Status</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">🎯 Model Performance</div>
                    <div class="metric-value {status_class}">{model_status}</div>
                    <div class="metric-detail">Accuracy: <strong>{r2_score*100:.2f}%</strong></div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(r2_score*100, 100)}%"></div>
                    </div>
                    <div class="metric-detail">RMSE: <strong>{metrics_data['ml_model_rmse']:.4f}</strong></div>
                    <div class="metric-detail">MAE: <strong>{metrics_data['ml_model_mae']:.4f}</strong></div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">🌐 API Status</div>
                    <div class="metric-value {api_status_class}">{api_status}</div>
                    <div class="metric-detail">Response Time: <strong>{metrics_data['api_response_time']:.0f}ms</strong></div>
                    <div class="metric-detail">Health Check: <span class="{api_status_class}">{'✅ PASSING' if metrics_data['api_health'] else '❌ FAILING'}</span></div>
                    <div class="metric-detail">
                        <a href="{MAIN_API_URL}/api/health" target="_blank" class="api-link">🔗 Test API Health</a>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">📊 Quick Stats</div>
                    <div class="metric-detail">Model Accuracy: <strong class="status-good">{r2_score*100:.2f}%</strong></div>
                    <div class="metric-detail">Prediction Error: <strong>{metrics_data['ml_model_rmse']:.2f} points</strong></div>
                    <div class="metric-detail">API Health: <strong class="{api_status_class}">{'HEALTHY' if metrics_data['api_health'] else 'UNHEALTHY'}</strong></div>
                    <div class="metric-detail">Last Check: <strong>{datetime.now().strftime('%H:%M:%S')}</strong></div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">🔗 API Endpoints</div>
                    <div class="metric-detail">
                        <a href="{MAIN_API_URL}/api/predict" target="_blank" class="api-link">📝 Prediction API</a>
                    </div>
                    <div class="metric-detail">
                        <a href="{MAIN_API_URL}/api/model-info" target="_blank" class="api-link">ℹ️ Model Info</a>
                    </div>
                    <div class="metric-detail">
                        <a href="/api/status" target="_blank" class="api-link">📊 Monitoring Status</a>
                    </div>
                    <div class="metric-detail">
                        <a href="/api/metrics" target="_blank" class="api-link">🔍 Prometheus Metrics</a>
                    </div>
                </div>
            </div>
            
            <div class="timestamp">
                🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh every 30 seconds
            </div>
        </div>
    </body>
    </html>
    """
    
    return dashboard_html

@app.route('/')
def home():
    """Redirect to dashboard"""
    return dashboard()

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
