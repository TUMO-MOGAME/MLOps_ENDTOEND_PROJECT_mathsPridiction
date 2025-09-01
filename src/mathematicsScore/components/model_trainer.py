import os
import pandas as pd
import pickle
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from src.mathematicsScore.logging import logger
from src.mathematicsScore.entity import ModelTrainerConfig

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        """
        Train the model using ElasticNet regression.
        """
        try:
            # Load the transformed training data
            logger.info(f"Loading training data from {self.config.train_data_path}")
            train_data = pd.read_csv(self.config.train_data_path)
            logger.info(f"Training data loaded with shape: {train_data.shape}")

            # Load the transformed test data
            logger.info(f"Loading test data from {self.config.test_data_path}")
            test_data = pd.read_csv(self.config.test_data_path)
            logger.info(f"Test data loaded with shape: {test_data.shape}")

            # Separate features and target
            target_column = self.config.target_column
            
            # Check if target column exists, if not use math_score
            if target_column not in train_data.columns:
                if 'math_score' in train_data.columns:
                    target_column = 'math_score'
                    logger.warning(f"Target column '{self.config.target_column}' not found, using 'math_score'")
                else:
                    raise ValueError(f"Neither '{self.config.target_column}' nor 'math_score' found in the data")

            # Split features and target for training data
            X_train = train_data.drop(columns=[target_column])
            y_train = train_data[target_column]

            # Split features and target for test data
            X_test = test_data.drop(columns=[target_column])
            y_test = test_data[target_column]

            logger.info(f"Training features shape: {X_train.shape}")
            logger.info(f"Training target shape: {y_train.shape}")
            logger.info(f"Test features shape: {X_test.shape}")
            logger.info(f"Test target shape: {y_test.shape}")

            # Initialize and train the ElasticNet model
            logger.info(f"Training ElasticNet model with alpha={self.config.alpha}, l1_ratio={self.config.l1_ratio}")
            model = ElasticNet(
                alpha=self.config.alpha,
                l1_ratio=self.config.l1_ratio,
                random_state=42
            )

            # Train the model
            model.fit(X_train, y_train)
            logger.info("Model training completed")

            # Save the trained model
            model_path = os.path.join(self.config.root_dir, self.config.model_name)
            logger.info(f"Saving model to {model_path}")

            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

            logger.info("Model saved successfully")

            # Save training info for evaluation stage
            training_info = {
                'model_path': model_path,
                'alpha': self.config.alpha,
                'l1_ratio': self.config.l1_ratio,
                'target_column': target_column,
                'feature_columns': list(X_train.columns),
                'train_data_shape': X_train.shape,
                'test_data_shape': X_test.shape
            }

            training_info_path = os.path.join(self.config.root_dir, 'training_info.pkl')
            with open(training_info_path, 'wb') as f:
                pickle.dump(training_info, f)

            logger.info(f"Training info saved to {training_info_path}")

            return {
                'model': model,
                'model_path': model_path,
                'training_info': training_info
            }

        except Exception as e:
            logger.error(f"Error in model training: {e}")
            raise e
