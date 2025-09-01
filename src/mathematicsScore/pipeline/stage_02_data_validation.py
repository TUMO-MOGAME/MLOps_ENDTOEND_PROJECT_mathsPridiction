
from src.mathematicsScore.config.configuration import ConfigurationManager
from src.mathematicsScore.components.data_validation import DataValidation
from src.mathematicsScore.logging import logger


class DataValidationPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            data_validation_config = config.get_data_validation_config()
            data_validation = DataValidation(data_validation_config)
            status = data_validation.validate_all_files_exist()
            logger.info(f"Validation status: {status}")
        except Exception as e:
            logger.error(f"Error occurred: {e}")


