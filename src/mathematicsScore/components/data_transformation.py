import os
import pandas as pd
import pickle
from src.mathematicsScore.logging import logger
from src.mathematicsScore.entity import DataTransformationConfig

class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config    
        
    def handle_missing_values(self, data):
        """
        Handle missing values in the dataset. 
        Numerical columns will be filled with the median, 
        categorical columns will be filled with the mode.
        """
        # Fill missing values for numerical columns with the median
        numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns
        for col in numerical_columns:
            data[col].fillna(data[col].median(), inplace=True)
        
        # Fill missing values for categorical columns with the mode
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if not data[col].mode().empty:
                data[col].fillna(data[col].mode()[0], inplace=True)
        
        return data
    
    def create_dummy_variables(self, data):
        """
        Convert categorical variables into dummy variables (one-hot encoding).
        """
        return pd.get_dummies(data, drop_first=True)
    
    def transform(self):
        """
        Perform data transformation steps on pre-split train and test datasets.
        Loads existing train_data.csv and test_data.csv, transforms them separately.
        """
        try:
            # Load the pre-split train and test data
            train_data_path = os.path.join("artifacts/data_ingestion", "train_data.csv")
            test_data_path = os.path.join("artifacts/data_ingestion", "test_data.csv")

            logger.info(f"Loading train data from {train_data_path}")
            train_data = pd.read_csv(train_data_path)
            logger.info(f"Train data loaded successfully with shape: {train_data.shape}")

            logger.info(f"Loading test data from {test_data_path}")
            test_data = pd.read_csv(test_data_path)
            logger.info(f"Test data loaded successfully with shape: {test_data.shape}")

            # Transform train data
            logger.info("Transforming train data...")
            train_data = self.handle_missing_values(train_data)
            train_data = self.create_dummy_variables(train_data)

            # Transform test data using the same transformations
            logger.info("Transforming test data...")
            test_data = self.handle_missing_values(test_data)
            test_data = self.create_dummy_variables(test_data)

            # Ensure both datasets have the same columns (important for dummy variables)
            # Get all columns from train data
            train_columns = set(train_data.columns)
            test_columns = set(test_data.columns)

            # Add missing columns to test data (fill with 0)
            missing_in_test = train_columns - test_columns
            for col in missing_in_test:
                test_data[col] = 0
                logger.info(f"Added missing column '{col}' to test data")

            # Add missing columns to train data (fill with 0)
            missing_in_train = test_columns - train_columns
            for col in missing_in_train:
                train_data[col] = 0
                logger.info(f"Added missing column '{col}' to train data")

            # Reorder columns to match
            train_data = train_data[sorted(train_data.columns)]
            test_data = test_data[sorted(test_data.columns)]

            # Save transformed data
            logger.info(f"Saving transformed train data to {self.config.transformed_train_path}")
            train_data.to_csv(self.config.transformed_train_path, index=False)

            logger.info(f"Saving transformed test data to {self.config.transformed_test_path}")
            test_data.to_csv(self.config.transformed_test_path, index=False)

            # Save preprocessor info (for future use)
            preprocessor_info = {
                'feature_columns': list(train_data.columns),
                'target_column': 'math_score' if 'math_score' in train_data.columns else None,
                'train_shape': train_data.shape,
                'test_shape': test_data.shape,
                'original_train_shape': (train_data.shape[0], len(pd.read_csv(train_data_path).columns)),
                'original_test_shape': (test_data.shape[0], len(pd.read_csv(test_data_path).columns))
            }

            with open(self.config.preprocessor_path, 'wb') as f:
                pickle.dump(preprocessor_info, f)

            logger.info(f"Data transformation completed successfully")
            logger.info(f"Transformed train data shape: {train_data.shape}")
            logger.info(f"Transformed test data shape: {test_data.shape}")

            return {
                'train_data': train_data,
                'test_data': test_data,
                'preprocessor_info': preprocessor_info
            }

        except Exception as e:
            logger.error(f"Error in data transformation: {e}")
            raise e
