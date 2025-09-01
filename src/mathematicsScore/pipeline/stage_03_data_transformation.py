
import os
from src.mathematicsScore.config.configuration import ConfigurationManager
from src.mathematicsScore.components.data_transformation import DataTransformation
from src.mathematicsScore.logging import logger

class DataTransformationPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            data_transformation_config = config.get_data_transformation_config()
            data_transformation = DataTransformation(config=data_transformation_config)
            result = data_transformation.transform()
            logger.info("Data transformation completed successfully")
        except Exception as e:
            logger.error(f"Error in data transformation pipeline: {e}")
            raise e


