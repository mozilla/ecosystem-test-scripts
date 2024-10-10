import logging
from config import Config
from uploader import GoogleSheetUploader

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load configuration
    config = Config()

    # Create uploader instance
    uploader = GoogleSheetUploader(config)

    # Process CSV files
    uploader.process_csv_files()

if __name__ == '__main__':
    main()
