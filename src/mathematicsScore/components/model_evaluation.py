import os
import pandas as pd
import pickle
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.mathematicsScore.logging import logger
from src.mathematicsScore.entity import ModelTrainerConfig

class ModelEvaluation:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def evaluate(self):
        """
        Evaluate the trained model using test data.
        """
        try:
            # Load the trained model
            model_path = os.path.join(self.config.root_dir, self.config.model_name)
            logger.info(f"Loading trained model from {model_path}")

            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            logger.info("Model loaded successfully")

            # Load training info
            training_info_path = os.path.join(self.config.root_dir, 'training_info.pkl')
            with open(training_info_path, 'rb') as f:
                training_info = pickle.load(f)

            target_column = training_info['target_column']

            # Load the transformed training data
            logger.info(f"Loading training data from {self.config.train_data_path}")
            train_data = pd.read_csv(self.config.train_data_path)
            logger.info(f"Training data loaded with shape: {train_data.shape}")

            # Load the transformed test data
            logger.info(f"Loading test data from {self.config.test_data_path}")
            test_data = pd.read_csv(self.config.test_data_path)
            logger.info(f"Test data loaded with shape: {test_data.shape}")

            # Check if target column exists, if not use math_score
            if target_column not in train_data.columns:
                if 'math_score' in train_data.columns:
                    target_column = 'math_score'
                    logger.warning(f"Target column '{training_info['target_column']}' not found, using 'math_score'")
                else:
                    raise ValueError(f"Neither '{training_info['target_column']}' nor 'math_score' found in the data")

            # Split features and target for training data
            X_train = train_data.drop(columns=[target_column])
            y_train = train_data[target_column]

            # Split features and target for test data
            X_test = test_data.drop(columns=[target_column])
            y_test = test_data[target_column]

            logger.info(f"Evaluation features shape: {X_test.shape}")
            logger.info(f"Evaluation target shape: {y_test.shape}")

            # Make predictions
            logger.info("Making predictions...")
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Calculate metrics
            logger.info("Calculating evaluation metrics...")
            train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)

            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)

            # Log metrics
            print( )
            logger.info("=== Model Performance Metrics ===")
            logger.info(f"Training RMSE: {train_rmse:.4f}")
            logger.info(f"Test RMSE: {test_rmse:.4f}")
            logger.info(f"Training MAE: {train_mae:.4f}")
            logger.info(f"Test MAE: {test_mae:.4f}")
            logger.info(f"Training R²: {train_r2:.4f}")
            logger.info(f"Test R²: {test_r2:.4f}")

            # Save evaluation metrics
            print( )
            metrics = {
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'alpha': training_info['alpha'],
                'l1_ratio': training_info['l1_ratio'],
                'target_column': target_column,
                'model_path': model_path
            }

            # Create evaluation directory if it doesn't exist
            evaluation_dir = os.path.join("artifacts", "model_evaluation")
            os.makedirs(evaluation_dir, exist_ok=True)

            metrics_path = os.path.join(evaluation_dir, 'evaluation_metrics.pkl')
            with open(metrics_path, 'wb') as f:
                pickle.dump(metrics, f)

            logger.info(f"Evaluation metrics saved to {metrics_path}")

            # Save metrics as JSON for easy reading
            import json
            metrics_json_path = os.path.join(evaluation_dir, 'evaluation_metrics.json')
            with open(metrics_json_path, 'w') as f:
                # Convert numpy types to Python types for JSON serialization
                json_metrics = {k: float(v) if isinstance(v, (np.float64, np.float32)) else v
                              for k, v in metrics.items()}
                json.dump(json_metrics, f, indent=4)

            logger.info(f"Evaluation metrics saved as JSON to {metrics_json_path}")
            logger.info("Model evaluation completed successfully")

            return {
                'metrics': metrics,
                'metrics_path': metrics_path
            }

        except Exception as e:
            logger.error(f"Error in model evaluation: {e}")
            raise e