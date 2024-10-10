import json
from configparser import ConfigParser, ExtendedInterpolation

class Config:
    def __init__(self, config_file='config.ini'):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(config_file)

        self.service_account_file = config.get('google_sheet_uploader', 'service_account_file')

        # Retrieve the mappings string
        mappings_str = config.get('google_sheet_uploader', 'mappings')

        # Parse the JSON string
        try:
            self.mappings = json.loads(mappings_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing mappings JSON: {e}")
