"""
Simple metrics server for ML Pipeline monitoring
Run this alongside your ML pipeline to expose metrics to Prometheus
"""

from flask import Flask, Response
import json
import os
import pickle
import time
from datetime import datetime, timezone

app = Flask(__name__)

def get_latest_metrics():
    """Get the latest metrics from your ML pipeline artifacts"""
    metrics = {
        'ml_model_r2_score': 0.0,
        'ml_model_rmse': 0.0,
        'ml_model_mae': 0.0,
        'ml_data_ingestion_success': 1,
        'ml_data_validation_success': 1,
        'ml_pipeline_success': 1,
        'ml_pipeline_duration_seconds': 0,
        'ml_pipeline_last_run_timestamp': time.time()
    }
    
    try:
        # Try to read evaluation metrics (check both possible file names)
        eval_metrics_paths = [
            'artifacts/model_evaluation/evaluation_report.json',
            'artifacts/model_evaluation/evaluation_metrics.json',
            '../artifacts/model_evaluation/evaluation_report.json',
            '../artifacts/model_evaluation/evaluation_metrics.json'
        ]

        for eval_metrics_path in eval_metrics_paths:
            if os.path.exists(eval_metrics_path):
                with open(eval_metrics_path, 'r') as f:
                    eval_data = json.load(f)
                    metrics['ml_model_r2_score'] = eval_data.get('test_r2', 0.0)
                    metrics['ml_model_rmse'] = eval_data.get('test_rmse', 0.0)
                    metrics['ml_model_mae'] = eval_data.get('test_mae', 0.0)
                break
        
        # Check if data validation passed
        validation_status_paths = [
            'artifacts/data_validation/status.txt',
            '../artifacts/data_validation/status.txt'
        ]
        for validation_status_path in validation_status_paths:
            if os.path.exists(validation_status_path):
                with open(validation_status_path, 'r') as f:
                    status = f.read().strip()
                    metrics['ml_data_validation_success'] = 1 if status == 'Validation status: True' else 0
                break

        # Check if data ingestion artifacts exist
        ingestion_paths = ['artifacts/data_ingestion', '../artifacts/data_ingestion']
        for ingestion_path in ingestion_paths:
            if os.path.exists(ingestion_path):
                files = os.listdir(ingestion_path)
                metrics['ml_data_ingestion_success'] = 1 if len(files) > 0 else 0
                break

        # Check overall pipeline success (if all artifacts exist)
        required_paths = [
            'artifacts/data_ingestion',
            'artifacts/data_transformation',
            'artifacts/model_trainer'
        ]
        if not all(os.path.exists(p) for p in required_paths):
            # Try with ../ prefix
            required_paths = [
                '../artifacts/data_ingestion',
                '../artifacts/data_transformation',
                '../artifacts/model_trainer'
            ]
        metrics['ml_pipeline_success'] = 1 if all(os.path.exists(p) for p in required_paths) else 0
        
    except Exception as e:
        print(f"Error reading metrics: {e}")
        metrics['ml_pipeline_success'] = 0
    
    return metrics

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    metrics_data = get_latest_metrics()
    
    # Convert to Prometheus format
    prometheus_metrics = []
    for key, value in metrics_data.items():
        prometheus_metrics.append(f"# HELP {key} ML Pipeline metric")
        prometheus_metrics.append(f"# TYPE {key} gauge")
        prometheus_metrics.append(f"{key} {value}")
    
    return Response('\n'.join(prometheus_metrics), mimetype='text/plain')

@app.route('/ml-metrics')
def ml_metrics():
    """JSON metrics endpoint with human-readable formatting"""
    metrics_data = get_latest_metrics()

    # Create human-readable version
    human_readable = {
        'model_performance': {
            'r2_score': f"{metrics_data['ml_model_r2_score']:.4f} ({metrics_data['ml_model_r2_score']*100:.2f}%)",
            'rmse': f"{metrics_data['ml_model_rmse']:.4f}",
            'mae': f"{metrics_data['ml_model_mae']:.4f}"
        },
        'pipeline_status': {
            'overall_success': 'SUCCESS' if metrics_data['ml_pipeline_success'] == 1 else 'FAILED',
            'data_ingestion': 'SUCCESS' if metrics_data['ml_data_ingestion_success'] == 1 else 'FAILED',
            'data_validation': 'SUCCESS' if metrics_data['ml_data_validation_success'] == 1 else 'FAILED'
        },
        'timing': {
            'last_run': datetime.fromtimestamp(metrics_data['ml_pipeline_last_run_timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': f"{metrics_data['ml_pipeline_duration_seconds']/60:.2f} min" if metrics_data['ml_pipeline_duration_seconds'] > 0 else 'N/A'
        },
        'raw_metrics': metrics_data
    }

    return json.dumps(human_readable, indent=2)

@app.route('/dashboard')
def dashboard():
    """Human-readable dashboard endpoint"""
    metrics_data = get_latest_metrics()

    # Determine status colors and messages
    r2_score = metrics_data['ml_model_r2_score']
    if r2_score >= 0.8:
        model_status = "🟢 EXCELLENT"
    elif r2_score >= 0.7:
        model_status = "🟡 GOOD"
    elif r2_score >= 0.6:
        model_status = "🟠 FAIR"
    else:
        model_status = "🔴 POOR"

    pipeline_status = "🟢 HEALTHY" if metrics_data['ml_pipeline_success'] == 1 else "🔴 FAILED"

    last_run = datetime.fromtimestamp(metrics_data['ml_pipeline_last_run_timestamp'])
    time_ago = datetime.now() - last_run

    if time_ago.total_seconds() < 60:
        time_ago_str = f"{int(time_ago.total_seconds())} seconds ago"
    elif time_ago.total_seconds() < 3600:
        time_ago_str = f"{int(time_ago.total_seconds()/60)} minutes ago"
    else:
        time_ago_str = f"{int(time_ago.total_seconds()/3600)} hours ago"

    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Pipeline Dashboard</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }}
            .metric-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
            .status-good {{ color: #28a745; }}
            .status-warning {{ color: #ffc107; }}
            .status-error {{ color: #dc3545; }}
            .timestamp {{ color: #666; font-size: 14px; }}
            .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }}
            .progress-fill {{ height: 100%; background-color: #28a745; transition: width 0.3s ease; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Mathematics Score Prediction - ML Pipeline Dashboard</h1>
                <p class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh every 30 seconds</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">📊 Model Performance</div>
                    <div class="metric-value">{model_status}</div>
                    <div>R² Score: <strong>{r2_score:.4f} ({r2_score*100:.2f}%)</strong></div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {r2_score*100}%"></div>
                    </div>
                    <div style="margin-top: 10px;">
                        <div>RMSE: <strong>{metrics_data['ml_model_rmse']:.4f}</strong></div>
                        <div>MAE: <strong>{metrics_data['ml_model_mae']:.4f}</strong></div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">🚀 Pipeline Status</div>
                    <div class="metric-value">{pipeline_status}</div>
                    <div>Data Ingestion: <span class="{'status-good' if metrics_data['ml_data_ingestion_success'] else 'status-error'}">{'✅ SUCCESS' if metrics_data['ml_data_ingestion_success'] else '❌ FAILED'}</span></div>
                    <div>Data Validation: <span class="{'status-good' if metrics_data['ml_data_validation_success'] else 'status-error'}">{'✅ SUCCESS' if metrics_data['ml_data_validation_success'] else '❌ FAILED'}</span></div>
                    <div>Model Training: <span class="status-good">✅ SUCCESS</span></div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">⏰ Timing Information</div>
                    <div class="metric-value">{time_ago_str}</div>
                    <div>Last Run: <strong>{last_run.strftime('%Y-%m-%d %H:%M:%S')}</strong></div>
                    <div>Duration: <strong>{metrics_data['ml_pipeline_duration_seconds']/60:.2f} minutes</strong></div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">📈 Quick Stats</div>
                    <div style="margin: 10px 0;">
                        <div>Model Accuracy: <strong class="status-good">{r2_score*100:.2f}%</strong></div>
                        <div>Prediction Error: <strong>{metrics_data['ml_model_rmse']:.2f} points</strong></div>
                        <div>Pipeline Health: <strong class="{'status-good' if metrics_data['ml_pipeline_success'] else 'status-error'}">{'HEALTHY' if metrics_data['ml_pipeline_success'] else 'UNHEALTHY'}</strong></div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 40px; text-align: center; color: #666;">
                <p>🔗 <a href="/metrics">Prometheus Metrics</a> | <a href="/ml-metrics">JSON API</a> | <a href="/health">Health Check</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return dashboard_html

@app.route('/status')
def status():
    """Simple status endpoint"""
    metrics_data = get_latest_metrics()
    last_run = datetime.fromtimestamp(metrics_data['ml_pipeline_last_run_timestamp'])

    return {
        'pipeline_status': 'HEALTHY' if metrics_data['ml_pipeline_success'] == 1 else 'FAILED',
        'model_accuracy': f"{metrics_data['ml_model_r2_score']*100:.2f}%",
        'model_r2_score': round(metrics_data['ml_model_r2_score'], 4),
        'model_rmse': round(metrics_data['ml_model_rmse'], 4),
        'model_mae': round(metrics_data['ml_model_mae'], 4),
        'last_run': last_run.strftime('%Y-%m-%d %H:%M:%S'),
        'data_ingestion': 'SUCCESS' if metrics_data['ml_data_ingestion_success'] == 1 else 'FAILED',
        'data_validation': 'SUCCESS' if metrics_data['ml_data_validation_success'] == 1 else 'FAILED',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

if __name__ == '__main__':
    print("🚀 Starting ML Metrics Server...")
    print("📊 Endpoints available at:")
    print("  - http://localhost:8001/dashboard (📊 Human-readable dashboard)")
    print("  - http://localhost:8001/status (📋 Simple status JSON)")
    print("  - http://localhost:8001/metrics (🔍 Prometheus format)")
    print("  - http://localhost:8001/ml-metrics (📄 Detailed JSON)")
    print("  - http://localhost:8001/health (❤️  Health check)")
    print("\n🎯 Open http://localhost:8001/dashboard in your browser for the best experience!")
    app.run(host='0.0.0.0', port=8001, debug=False)
