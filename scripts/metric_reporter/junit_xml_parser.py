# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing test suite results from JUnit XML content."""

import logging
import re
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as ElementTree
from pydantic import BaseModel, ValidationError

from scripts.common.error import BaseError


class JUnitXmlProperty(BaseModel):
    """Represents a property of a test case."""

    name: str
    value: str


class JUnitXmlSkipped(BaseModel):
    """Represents a skipped test case."""

    reason: str | None = None


class JUnitXmlFailure(BaseModel):
    """Represents a failure of a test case."""

    message: str
    type: str | None = None
    text: str | None = None


class JUnitXmlSystemOut(BaseModel):
    """Represents system out information."""

    text: str | None = None


class JUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str | None = None
    time: float | None = None
    properties: list[JUnitXmlProperty] | None = None
    skipped: JUnitXmlSkipped | None = None
    failure: JUnitXmlFailure | None = None
    system_out: JUnitXmlSystemOut | None = None


class JUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    timestamp: str | None = None
    hostname: str | None = None
    tests: int
    failures: int
    skipped: int | None = None
    time: float | None = None
    errors: int | None = None
    test_cases: list[JUnitXmlTestCase]


class JUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    id: str | None = None
    name: str | None = None
    tests: int | None = None
    failures: int | None = None
    skipped: int | None = None
    errors: int | None = None
    time: float | None = None
    timestamp: str | None = None
    test_suites: list[JUnitXmlTestSuite] = []


class JUnitXmlJobTestSuites(BaseModel):
    """Represents the test suite results for a CircleCI job."""

    job: int
    test_suites: list[JUnitXmlTestSuites]


class JUnitXmlParserError(BaseError):
    """Custom exception for errors raised by the JUnit XML parser."""

    pass


class JUnitXmlParser:
    """Parses JUnit XML files."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def _normalize_xml_content(content: str) -> str:
        return re.sub(r"\x00", "", content)

    def _parse_test_case(self, test_case, xml_file_path: Path) -> dict[str, Any]:
        test_case_dict: dict[str, Any] = test_case.attrib
        for child in test_case:
            tag: str = child.tag
            if tag == "properties":
                test_case_dict["properties"] = [prop.attrib for prop in child]
            elif tag == "skipped":
                test_case_dict["skipped"] = child.attrib
            elif tag == "system-out":
                test_case_dict["system_out"] = {"text": child.text}
            elif tag == "failure":
                test_case_dict["failure"] = child.attrib
                test_case_dict["failure"]["text"] = child.text
            else:
                error_msg = f"Could not parse XML file, {xml_file_path}, unexpected tag: {tag}"
                self.logger.error(error_msg)
                raise JUnitXmlParserError(error_msg)
        return test_case_dict

    def _parse_test_suite(self, test_suite, xml_file_path: Path) -> dict[str, Any]:
        test_suite_dict: dict[str, Any] = test_suite.attrib
        test_suite_dict["test_cases"] = [
            self._parse_test_case(test_case, xml_file_path) for test_case in test_suite
        ]
        return test_suite_dict

    def parse(self, artifact_path: Path) -> list[JUnitXmlJobTestSuites]:
        """Parse JUnit XML content from the specified directory.

        Args:
            artifact_path (Path): The path to the directory containing the JUnit XML test files.

        Returns:
            list[JUnitXmlJobTestSuites]: A list of parsed `JUnitXMLJobTestSuites` objects.

        Raises:
            JUnitXmlParserError: If there is an error reading or parsing the XML files.
        """
        artifact_list: list[JUnitXmlJobTestSuites] = []
        job_paths: list[Path] = sorted(artifact_path.iterdir())
        for job_path in job_paths:
            job_number = int(job_path.name)
            test_suites_list: list[JUnitXmlTestSuites] = []
            artifact_file_paths: list[Path] = sorted(job_path.glob("*.xml"))
            for artifact_file_path in artifact_file_paths:
                self.logger.info(f"Parsing {artifact_file_path}")
                try:
                    with artifact_file_path.open() as xml_file:
                        content: str = xml_file.read()
                        normalized_content: str = self._normalize_xml_content(content)

                        root = ElementTree.fromstring(normalized_content)
                        test_suites_dict: dict[str, Any] = root.attrib
                        test_suites_dict["test_suites"] = [
                            self._parse_test_suite(test_suite, artifact_file_path)
                            for test_suite in root
                        ]
                        test_suites = JUnitXmlTestSuites(**test_suites_dict)

                        test_suites_list.append(test_suites)
                except (OSError, ElementTree.ParseError, ValidationError) as error:
                    error_mapping: dict[type, str] = {
                        OSError: f"Error reading the file {artifact_file_path}",
                        ElementTree.ParseError: f"Invalid XML format for file {artifact_file_path}",
                        ValidationError: f"Unexpected value or schema in file {artifact_file_path}",
                    }
                    error_msg = error_mapping[type(error)]
                    self.logger.error(error_msg, exc_info=error)
                    raise JUnitXmlParserError(error_msg, error)
            artifact_list.append(
                JUnitXmlJobTestSuites(job=job_number, test_suites=test_suites_list)
            )
        return artifact_list
