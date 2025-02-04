# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing test suite results from JUnit XML content."""

import logging
from pathlib import Path
from typing import Any

import xmltodict
from pydantic import BaseModel, ValidationError, TypeAdapter

from scripts.metric_reporter.parser.base_parser import ArtifactFile, BaseParser, ParserError


class JestJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str
    time: float
    skipped: str | None = None
    failure: str | None = None


class JestJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    timestamp: str
    tests: int
    failures: int
    skipped: int
    time: float
    errors: int
    test_cases: list[JestJUnitXmlTestCase]


class JestJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    name: str
    tests: int
    failures: int
    errors: int
    time: float
    test_suites: list[JestJUnitXmlTestSuite]


class MochaJUnitXmlFailure(BaseModel):
    """Represents a failure of a test case."""

    message: str
    type: str
    text: str | None = None


class MochaJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str
    time: float
    skipped: str | None = None
    failure: MochaJUnitXmlFailure | None = None


class MochaJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    timestamp: str
    tests: int
    failures: int
    file: str | None = None
    time: float
    test_cases: list[MochaJUnitXmlTestCase] | None = []


class MochaJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    name: str
    tests: int
    failures: int
    skipped: int | None = None
    time: float
    test_suites: list[MochaJUnitXmlTestSuite] | None = []


class NextestJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str
    timestamp: str
    time: float | None = None


class NextestJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    tests: int
    failures: int
    skipped: int
    errors: int
    test_cases: list[NextestJUnitXmlTestCase]


class NextestJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    name: str
    tests: int
    failures: int
    errors: int
    time: float
    timestamp: str
    uuid: str
    test_suites: list[NextestJUnitXmlTestSuite]


class PlaywrightJUnitXmlProperty(BaseModel):
    """Represents a property of a test case."""

    name: str
    value: str
    text: str | None = None


class PlaywrightJUnitXmlProperties(BaseModel):
    """Represents a property of a test case."""

    property: list[PlaywrightJUnitXmlProperty]


class PlaywrightJUnitXmlFailure(BaseModel):
    """Represents a failure of a test case."""

    message: str
    type: str
    text: str | None = None


class PlaywrightJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str | None = None
    time: float | None = None
    properties: PlaywrightJUnitXmlProperties | None = None
    skipped: str | None = None
    failure: PlaywrightJUnitXmlFailure | None = None
    system_out: str | None = None


class PlaywrightJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    timestamp: str
    hostname: str
    tests: int
    failures: int
    skipped: int
    time: float
    errors: int
    test_cases: list[PlaywrightJUnitXmlTestCase]


class PlaywrightJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    id: str
    name: str
    tests: int
    failures: int
    skipped: int
    errors: int
    time: float
    test_suites: list[PlaywrightJUnitXmlTestSuite]


class PytestJUnitXmlSkipped(BaseModel):
    """Represents a skipped test case."""

    message: str
    type: str
    text: str | None = None


class PytestJUnitXmlFailure(BaseModel):
    """Represents a failure of a test case."""

    message: str
    text: str | None = None


class PytestJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str
    classname: str
    time: float
    skipped: PytestJUnitXmlSkipped | None = None
    failure: PytestJUnitXmlFailure | None = None


class PytestJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    timestamp: str
    hostname: str
    tests: int
    failures: int
    skipped: int
    time: float
    errors: int
    test_cases: list[PytestJUnitXmlTestCase]


class PytestJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    test_suites: list[PytestJUnitXmlTestSuite]


class TapJUnitXmlTestCase(BaseModel):
    """Represents a test case in a test suite."""

    name: str


class TapJUnitXmlTestSuite(BaseModel):
    """Represents a test suite containing multiple test cases."""

    name: str
    tests: int
    failures: int
    errors: int | None = None
    test_cases: list[TapJUnitXmlTestCase]


class TapJUnitXmlTestSuites(BaseModel):
    """Represents a collection of test suites."""

    test_suites: list[TapJUnitXmlTestSuite]


JUnitXmlTestSuites = (
    JestJUnitXmlTestSuites
    | MochaJUnitXmlTestSuites
    | NextestJUnitXmlTestSuites
    | PlaywrightJUnitXmlTestSuites
    | PytestJUnitXmlTestSuites
    | TapJUnitXmlTestSuites
)


class JUnitXmlJobTestSuites(BaseModel):
    """Represents test results from one or more JUnit XML files for a test run."""

    job: int
    job_timestamp: str
    test_suites: list[JUnitXmlTestSuites] = []


class JUnitXmlGroup(BaseModel):
    """Represents test results for a repository/workflow/test_suite."""

    repository: str
    workflow: str
    test_suite: str
    junit_xmls: list[JUnitXmlJobTestSuites]


class JUnitXmlParser(BaseParser):
    """Parses JUnit XML files."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def _get_junit_xml(
        file: ArtifactFile, junit_xml_groups: list[JUnitXmlGroup]
    ) -> JUnitXmlJobTestSuites:
        if junit_xml_group := next(
            (
                group
                for group in junit_xml_groups
                if group.repository == file.repository
                and group.workflow == file.workflow
                and group.test_suite == file.test_suite
            ),
            None,
        ):
            if not (
                junit_xml := next(
                    (
                        junit_xmls
                        for junit_xmls in junit_xml_group.junit_xmls
                        if junit_xmls.job == file.job_number
                        and junit_xmls.job_timestamp == file.job_timestamp
                    ),
                    None,
                )
            ):
                junit_xml = JUnitXmlJobTestSuites(
                    job=file.job_number, job_timestamp=file.job_timestamp
                )
                junit_xml_group.junit_xmls.append(junit_xml)
        else:
            junit_xml = JUnitXmlJobTestSuites(
                job=file.job_number, job_timestamp=file.job_timestamp
            )
            junit_xml_group = JUnitXmlGroup(
                repository=file.repository,
                workflow=file.workflow,
                test_suite=file.test_suite,
                junit_xmls=[junit_xml],
            )
            junit_xml_groups.append(junit_xml_group)
        return junit_xml

    @staticmethod
    def _parse_test_suites(artifact_file_path: Path) -> JUnitXmlTestSuites:
        def postprocessor(path, key, value):
            key_mapping = {
                "testsuite": "test_suites",
                "testcase": "test_cases",
                "system-out": "system_out",  # Playwright
                "disabled": "skipped",  # Nextest skipped == disabled
                "#text": "text",
            }
            key = key_mapping.get(key, key)
            return key, value

        with artifact_file_path.open() as xml_file:
            content: str = xml_file.read()
            test_suites_dict: dict[str, Any] = xmltodict.parse(
                content,
                attr_prefix="",
                postprocessor=postprocessor,
                force_list=["test_suites", "test_cases", "property"],
            )
            adapter: TypeAdapter[JUnitXmlTestSuites] = TypeAdapter(JUnitXmlTestSuites)
            test_suites: JUnitXmlTestSuites = adapter.validate_python(
                test_suites_dict["testsuites"]
            )
            return test_suites

    def parse(self, artifact_file_paths: list[Path]) -> list[JUnitXmlGroup]:
        """Parse JUnit XML content from the specified directory.

        Args:
            artifact_file_paths (Path): Paths of the JUnit XML test files.

        Returns:
            list[JUnitXmlGroup]: A list of parsed JUnit XML files grouped by repository, workflow
                                 and test suite.

        Raises:
            ParserError: If there is an error reading or parsing the XML files.
        """
        junit_xml_groups: list[JUnitXmlGroup] = []
        for artifact_file_path in artifact_file_paths:
            self.logger.info(f"Parsing {artifact_file_path}")
            file: ArtifactFile = self._parse_artifact_file_name(artifact_file_path)
            junit_xml: JUnitXmlJobTestSuites = self._get_junit_xml(file, junit_xml_groups)
            try:
                test_suites: JUnitXmlTestSuites = self._parse_test_suites(file.path)
                junit_xml.test_suites.append(test_suites)
            except (OSError, ValidationError) as error:
                error_mapping: dict[type, str] = {
                    OSError: f"Error reading the file {artifact_file_path}",
                    ValidationError: f"Unexpected value or schema in file {artifact_file_path}",
                }
                error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
                self.logger.error(error_msg, exc_info=error)
                raise ParserError(error_msg) from error
        return junit_xml_groups
