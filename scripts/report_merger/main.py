# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Report Merger."""

import argparse
import logging
from pathlib import Path

from scripts.report_merger.config import Config
from scripts.report_merger.report_merger import ReportMerger

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(config_file: str = "config.ini") -> None:
    """Run the Report Merger.

    Args:
        config_file (str): Path to the configuration file.
                           Defaults to 'ecosystem-test-scripts/config.ini'.
    """
    try:
        logger.info(f"Starting Report Merger with configuration file: {config_file}")
        config = Config(config_file)
        for (
            merged_report_file_name,
            report_file_names,
        ) in config.metric_reporter_config.mappings.items():
            logger.info(f"Merging Reports for {merged_report_file_name}")
            report_file_paths: list[Path] = [
                Path(config.metric_reporter_config.reports_dir) / file_name
                for file_name in report_file_names
            ]
            merged_report_file_path: Path = (
                Path(config.metric_reporter_config.merged_reports_dir) / merged_report_file_name
            )
            merger = ReportMerger(report_file_paths)
            merger.output_csv(merged_report_file_path)
        logger.info("Reporting complete")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Merge Reports")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    parser_args = parser.parse_args()
    main(parser_args.config)
