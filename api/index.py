"""
Main API endpoint for Vercel deployment
"""

from flask import Flask, request, jsonify
import pickle
import numpy as np
import os
import json
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Model paths - adjusted for Vercel deployment structure
MODEL_PATH = 'artifacts/model_trainer/model.pkl'
TRAINING_INFO_PATH = 'artifacts/model_trainer/training_info.pkl'
PREPROCESSOR_PATH = 'artifacts/data_transformation/preprocessor.pkl'

# Global variables to cache model and training info
_model = None
_training_info = None

def load_model_and_info():
    """Load the trained model and training info"""
    global _model, _training_info

    if _model is not None and _training_info is not None:
        return _model, _training_info

    try:
        # Load training info first to get feature order
        if os.path.exists(TRAINING_INFO_PATH):
            with open(TRAINING_INFO_PATH, 'rb') as f:
                _training_info = pickle.load(f)
            print(f"Training info loaded: {_training_info}")
        else:
            print(f"Training info not found at {TRAINING_INFO_PATH}")
            return None, None

        # Load the model
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
            print(f"Model loaded successfully")
            return _model, _training_info
        else:
            print(f"Model not found at {MODEL_PATH}")
            return None, None

    except Exception as e:
        print(f"Error loading model and info: {e}")
        return None, None

def preprocess_input(data, training_info):
    """Preprocess input data to match exact training format"""
    try:
        if training_info is None:
            print("No training info available, using default preprocessing")
            return None

        # Get the exact feature order from training
        feature_columns = training_info['feature_columns']
        print(f"Expected features: {feature_columns}")

        # Create feature vector in exact order
        features = []

        for feature in feature_columns:
            if feature == 'gender_male':
                features.append(1 if data.get('gender') == 'male' else 0)
            elif feature == 'lunch_standard':
                features.append(1 if data.get('lunch') == 'standard' else 0)
            elif feature == "parental_level_of_education_bachelor's degree":
                features.append(1 if data.get('parental_level_of_education') == "bachelor's degree" else 0)
            elif feature == 'parental_level_of_education_high school':
                features.append(1 if data.get('parental_level_of_education') == 'high school' else 0)
            elif feature == "parental_level_of_education_master's degree":
                features.append(1 if data.get('parental_level_of_education') == "master's degree" else 0)
            elif feature == 'parental_level_of_education_some college':
                features.append(1 if data.get('parental_level_of_education') == 'some college' else 0)
            elif feature == 'parental_level_of_education_some high school':
                features.append(1 if data.get('parental_level_of_education') == 'some high school' else 0)
            elif feature == 'race_ethnicity_group B':
                features.append(1 if data.get('race_ethnicity') == 'group B' else 0)
            elif feature == 'race_ethnicity_group C':
                features.append(1 if data.get('race_ethnicity') == 'group C' else 0)
            elif feature == 'race_ethnicity_group D':
                features.append(1 if data.get('race_ethnicity') == 'group D' else 0)
            elif feature == 'race_ethnicity_group E':
                features.append(1 if data.get('race_ethnicity') == 'group E' else 0)
            elif feature == 'reading_score':
                features.append(float(data.get('reading_score', 0)))
            elif feature == 'test_preparation_course_none':
                features.append(1 if data.get('test_preparation_course') == 'none' else 0)
            elif feature == 'writing_score':
                features.append(float(data.get('writing_score', 0)))
            else:
                # Unknown feature, add 0
                features.append(0)
                print(f"Unknown feature: {feature}")

        print(f"Processed features: {features}")
        return np.array([features])

    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    try:
        return jsonify({
            'message': 'ML Pipeline API',
            'status': 'running',
            'endpoints': {
                'predict': '/api/predict (POST)',
                'health': '/api/health (GET)',
                'predict_alt': '/predict (POST)',
                'health_alt': '/health (GET)'
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/predict', methods=['POST'])
@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint using the actual trained model"""
    try:
        # Get input data
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No input data provided',
                'status': 'error'
            }), 400

        print(f"Received prediction request: {data}")

        # Load model and training info
        model, training_info = load_model_and_info()

        if model is None or training_info is None:
            # Fallback to intelligent mock prediction
            reading = float(data.get('reading_score', 50))
            writing = float(data.get('writing_score', 50))
            base_score = (reading + writing) / 2

            # Add some realistic variation based on other factors
            if data.get('test_preparation_course') == 'completed':
                base_score += 5
            if data.get('lunch') == 'free/reduced':
                base_score -= 3
            if data.get('parental_level_of_education') in ["bachelor's degree", "master's degree"]:
                base_score += 4

            prediction = max(0, min(100, base_score + np.random.normal(0, 3)))

            return jsonify({
                'prediction': float(prediction),
                'input_data': data,
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'model_used': 'fallback_intelligent_mock',
                'note': 'Using intelligent fallback prediction (model not available)'
            })

        # Preprocess input using training info
        processed_data = preprocess_input(data, training_info)

        if processed_data is None:
            return jsonify({
                'error': 'Failed to preprocess input data',
                'status': 'error'
            }), 400

        # Make prediction using the actual trained model
        prediction = model.predict(processed_data)[0]

        print(f"Model prediction: {prediction}")

        return jsonify({
            'prediction': float(prediction),
            'input_data': data,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'model_used': 'trained_elasticnet',
            'model_info': {
                'alpha': training_info.get('alpha'),
                'l1_ratio': training_info.get('l1_ratio'),
                'features_used': len(training_info.get('feature_columns', []))
            }
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check model and training info availability
        model, training_info = load_model_and_info()

        model_status = {
            'model_file_exists': os.path.exists(MODEL_PATH),
            'training_info_exists': os.path.exists(TRAINING_INFO_PATH),
            'model_loaded': model is not None,
            'training_info_loaded': training_info is not None
        }

        if training_info:
            model_status['model_details'] = {
                'target_column': training_info.get('target_column'),
                'feature_count': len(training_info.get('feature_columns', [])),
                'alpha': training_info.get('alpha'),
                'l1_ratio': training_info.get('l1_ratio')
            }

        return jsonify({
            'status': 'healthy',
            'model_status': model_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# This is the entry point for Vercel
# Vercel will automatically handle the WSGI interface
if __name__ == '__main__':
    app.run(debug=True)
