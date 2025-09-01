"""
Vercel API endpoint for ML model predictions
This will be deployed as the main user-facing API
"""

from flask import Flask, request, jsonify
import dill
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
                model = dill.load(f)
            return model
        else:
            return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def preprocess_input(data):
    """Preprocess input data to match training format"""
    # Convert input to numpy array format expected by the model
    # This is a simplified version - you may need to adjust based on your actual preprocessing

    # Expected features (adjust based on your model's training features)
    expected_features = [
        'writing_score', 'reading_score', 'gender_male',
        'race_ethnicity_group_B', 'race_ethnicity_group_C',
        'race_ethnicity_group_D', 'race_ethnicity_group_E',
        'parental_level_of_education_bachelor_degree',
        'parental_level_of_education_high_school',
        'parental_level_of_education_master_degree',
        'parental_level_of_education_some_college',
        'parental_level_of_education_some_high_school',
        'lunch_standard', 'test_preparation_course_none'
    ]

    # Create feature vector
    features = []
    for feature in expected_features:
        if feature in data:
            features.append(data[feature])
        else:
            features.append(0)  # Default value for missing features

    return np.array([features])

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
