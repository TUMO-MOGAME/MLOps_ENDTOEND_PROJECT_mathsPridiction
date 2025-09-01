from src.mathematicsScore.config.configuration import ConfigurationManager
from src.mathematicsScore.components.model_trainer import ModelTrainer
from src.mathematicsScore.logging import logger

class ModelTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            model_trainer_config = config.get_model_trainer_config()
            model_trainer = ModelTrainer(config=model_trainer_config)
            model_trainer.train()
            logger.info("Model training completed successfully")
        except Exception as e:
            logger.error(f"Error in model training pipeline: {e}")
            raise e