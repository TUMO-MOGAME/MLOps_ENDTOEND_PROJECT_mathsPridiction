"""
Main API endpoint for Vercel deployment
"""

from flask import Flask, request, jsonify
import pickle
import numpy as np
import os
import json
from datetime import datetime

app = Flask(__name__)

# Load the trained model
MODEL_PATH = '../artifacts/model_trainer/model.pkl'
PREPROCESSOR_PATH = '../artifacts/data_transformation/preprocessor.pkl'

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
    # Convert input to numpy array format expected by the model
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

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'ML Pipeline API',
        'status': 'running',
        'endpoints': {
            'predict': '/api/predict (POST)',
            'health': '/api/health (GET)',
            'model-info': '/api/model-info (GET)'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    model = load_model()
    return jsonify({
        'status': 'healthy' if model is not None else 'unhealthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
