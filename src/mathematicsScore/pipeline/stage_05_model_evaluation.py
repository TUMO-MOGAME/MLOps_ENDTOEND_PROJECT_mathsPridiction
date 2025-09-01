from src.mathematicsScore.config.configuration import ConfigurationManager
from src.mathematicsScore.components.model_evaluation import ModelEvaluation
from src.mathematicsScore.logging import logger

class ModelEvaluationPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            model_trainer_config = config.get_model_trainer_config()
            model_evaluation = ModelEvaluation(config=model_trainer_config)
            result = model_evaluation.evaluate()
            logger.info("Model evaluation completed successfully")
        except Exception as e:
            logger.error(f"Error in model evaluation pipeline: {e}")
            raise e