from src.mathematicsScore.config.configuration import ConfigurationManager
from src.mathematicsScore.logging import logger
from src.mathematicsScore.components.data_ingestion import DataIngestion

class DataIngestionPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config = ConfigurationManager()
            data_ingestion_config = config.get_data_ingestion_config()
            data_ingestion = DataIngestion(data_ingestion_config)
            logger.info(f"Data ingestion config: {data_ingestion_config}")

            # Actually perform the data ingestion
            data_ingestion.ingest_data_from_rawdata_folder()
            logger.info("Data ingestion completed successfully")
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise e