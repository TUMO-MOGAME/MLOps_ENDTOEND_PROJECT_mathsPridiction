import os
import urllib.request as request
from src.mathematicsScore.logging import logger
from src.mathematicsScore.utils.common import get_size
from pathlib import Path
from src.mathematicsScore.entity import DataIngestionConfig
import os
import pandas as pd


class DataIngestion:
    """Class to handle data ingestion from the 'RAWDATA' folder."""

    def __init__(self, config: DataIngestionConfig):
        """Initializes the DataIngestion class with the configuration."""
        self.config = config
        self.rawdata_folder_path = self.config.source_URL
    
    def check_rawdata_folder_exists(self):
        """Checks if the RAWDATA folder exists."""
        if not os.path.exists(self.rawdata_folder_path):
            raise FileNotFoundError(f"The folder 'RAWDATA' does not exist at path: {self.rawdata_folder_path}")
    
    def list_files_in_rawdata(self):
        """Lists all files in the RAWDATA folder."""
        return os.listdir(self.rawdata_folder_path)
    
    def read_csv_file(self, file_path):
        """Reads a CSV file into a pandas dataframe."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def ingest_data_from_rawdata_folder(self):
        """Ingests data from all CSV files in the RAWDATA folder."""
        self.check_rawdata_folder_exists()  # Check if the folder exists
        files = self.list_files_in_rawdata()  # Get list of files in the RAWDATA folder
        
        # Initialize an empty list to store dataframes info
        processed_files = []

        # Loop over each file in the folder
        for file in files:
            file_path = os.path.join(self.rawdata_folder_path, file)

            # Only process CSV files
            if file.endswith('.csv'):
                logger.info(f"Reading data from {file_path}")
                df = self.read_csv_file(file_path)  # Read the CSV file

                if df is not None:  # Ensure the file was read successfully
                    # Prepare the output file path
                    output_file_path = os.path.join(self.config.root_dir, file)
                    
                    # Check if the file already exists to avoid overwriting
                    if os.path.exists(output_file_path):
                        logger.warning(f"{file} already exists in the output folder. It will be overwritten.")

                    # Save the CSV to the output folder
                    df.to_csv(output_file_path, index=False)
                    logger.info(f"Saved {file} to {output_file_path} with {len(df)} rows")

                    # Append processed file details to the list
                    processed_files.append({
                        'filename': file,
                        'path': output_file_path,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'dataframe': df
                    })
                else:
                    logger.error(f"Skipping {file} due to read error.")

        logger.info(f"Data ingestion completed. Processed {len(processed_files)} files.")
        return processed_files
