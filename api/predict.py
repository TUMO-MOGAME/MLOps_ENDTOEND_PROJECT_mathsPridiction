"""
Vercel API endpoint for ML model predictions
This will be deployed as the main user-facing API
"""

from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

app = Flask(__name__)

# Load the trained model (you'll need to include this in deployment)
MODEL_PATH = 'artifacts/model_trainer/model.pkl'
PREPROCESSOR_PATH = 'artifacts/data_transformation/preprocessor.pkl'

def load_model():
    """Load the trained model"""
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            return model
        else:
            return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def preprocess_input(data):
    """Preprocess input data to match training format"""
    # Convert to DataFrame
    df = pd.DataFrame([data])
    
    # Apply the same transformations as in training
    # (You'll need to adapt this based on your actual preprocessing)
    df = pd.get_dummies(df, drop_first=True)
    
    return df

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        # Get input data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No input data provided',
                'status': 'error'
            }), 400
        
        # Load model
        model = load_model()
        if model is None:
            return jsonify({
                'error': 'Model not available',
                'status': 'error'
            }), 500
        
        # Preprocess input
        processed_data = preprocess_input(data)
        
        # Make prediction
        prediction = model.predict(processed_data)[0]
        
        # Log prediction for monitoring
        log_prediction(data, prediction)
        
        return jsonify({
            'prediction': float(prediction),
            'input_data': data,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    model = load_model()
    return jsonify({
        'status': 'healthy' if model is not None else 'unhealthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        # Load evaluation metrics
        eval_path = 'artifacts/model_evaluation/evaluation_report.json'
        if os.path.exists(eval_path):
            with open(eval_path, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = {}
        
        return jsonify({
            'model_metrics': metrics,
            'model_available': load_model() is not None,
            'last_updated': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def log_prediction(input_data, prediction):
    """Log prediction for monitoring (in production, send to monitoring service)"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'input': input_data,
        'prediction': float(prediction),
        'model_version': '1.0'
    }
    
    # In production, you'd send this to your monitoring service
    # For now, we'll just print it
    print(f"PREDICTION_LOG: {json.dumps(log_entry)}")

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
