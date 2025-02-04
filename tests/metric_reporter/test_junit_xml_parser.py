# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the JUnitXmlParser module."""

from pathlib import Path

import pytest

from scripts.metric_reporter.parser.junit_xml_parser import (
    JestJUnitXmlTestSuites,
    JestJUnitXmlTestCase,
    JestJUnitXmlTestSuite,
    JUnitXmlGroup,
    JUnitXmlJobTestSuites,
    JUnitXmlParser,
    MochaJUnitXmlFailure,
    MochaJUnitXmlTestSuites,
    MochaJUnitXmlTestSuite,
    MochaJUnitXmlTestCase,
    NextestJUnitXmlTestSuites,
    NextestJUnitXmlTestSuite,
    NextestJUnitXmlTestCase,
    PlaywrightJUnitXmlFailure,
    PlaywrightJUnitXmlProperty,
    PlaywrightJUnitXmlTestSuites,
    PlaywrightJUnitXmlTestSuite,
    PlaywrightJUnitXmlTestCase,
    PytestJUnitXmlFailure,
    PytestJUnitXmlSkipped,
    PytestJUnitXmlTestSuite,
    PytestJUnitXmlTestSuites,
    PytestJUnitXmlTestCase,
    TapJUnitXmlTestSuites,
    TapJUnitXmlTestSuite,
    TapJUnitXmlTestCase,
    PlaywrightJUnitXmlProperties,
)
from tests.metric_reporter.conftest import REPOSITORY, TEST_SUITE, WORKFLOW

EXPECTED_JEST = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-07-13T00:21:53Z",
                test_suites=[
                    JestJUnitXmlTestSuites(
                        name="jest tests",
                        tests=1,
                        failures=1,
                        errors=0,
                        time=0.017,
                        test_suites=[
                            JestJUnitXmlTestSuite(
                                name="useCheckboxStateResult",
                                timestamp="2024-07-13T00:21:53",
                                tests=1,
                                failures=1,
                                skipped=0,
                                time=0.017,
                                errors=0,
                                test_cases=[
                                    JestJUnitXmlTestCase(
                                        name=(
                                            'useInfoBoxMessage coupon type is "repeating" plan interval '
                                            "equal to coupon duration"
                                        ),
                                        classname=(
                                            'useInfoBoxMessage coupon type is "repeating" plan interval '
                                            "equal to coupon duration"
                                        ),
                                        time=0.017,
                                        failure="Error: expect(element).not.toBeInTheDocument()",
                                    )
                                ],
                            )
                        ],
                    ),
                    JestJUnitXmlTestSuites(
                        name="jest tests",
                        tests=1,
                        failures=0,
                        errors=0,
                        time=0.0,
                        test_suites=[
                            JestJUnitXmlTestSuite(
                                name="#integration - FirestoreService",
                                timestamp="2024-05-18T00:21:34",
                                tests=1,
                                failures=0,
                                skipped=1,
                                time=0.0,
                                errors=0,
                                test_cases=[
                                    JestJUnitXmlTestCase(
                                        name="#integration - FirestoreService should be defined",
                                        classname="#integration - FirestoreService should be defined",
                                        time=0.0,
                                    )
                                ],
                            )
                        ],
                    ),
                    JestJUnitXmlTestSuites(
                        name="jest tests",
                        tests=1,
                        failures=0,
                        errors=0,
                        time=0.042,
                        test_suites=[
                            JestJUnitXmlTestSuite(
                                name="lib/amplitude",
                                timestamp="2024-07-19T00:18:01",
                                tests=1,
                                failures=0,
                                skipped=0,
                                time=0.042,
                                errors=0,
                                test_cases=[
                                    JestJUnitXmlTestCase(
                                        name="lib/amplitude logs a correctly formatted message",
                                        classname="lib/amplitude logs a correctly formatted message",
                                        time=0.042,
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
]

EXPECTED_MOCHA = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-07-19T00:18:31Z",
                test_suites=[
                    MochaJUnitXmlTestSuites(
                        name="Mocha Tests",
                        tests=1,
                        failures=1,
                        time=0.002,
                        test_suites=[
                            MochaJUnitXmlTestSuite(
                                name="deleteUnverifiedAccounts",
                                timestamp="2024-07-19T00:18:31",
                                tests=1,
                                failures=1,
                                file=(
                                    "/home/circleci/project/packages/fxa-auth-server/test/local/routes/"
                                    "cloud-scheduler.js"
                                ),
                                time=0.002,
                                test_cases=[
                                    MochaJUnitXmlTestCase(
                                        name=(
                                            "CloudSchedulerHandler deleteUnverifiedAccounts should call "
                                            "processAccountDeletionInRange with correct parameters"
                                        ),
                                        classname=(
                                            "should call processAccountDeletionInRange with correct "
                                            "parameters"
                                        ),
                                        time=0.002,
                                        failure=MochaJUnitXmlFailure(
                                            message=(
                                                "expected processAccountDeletionInRange to be called once "
                                                "and with exact arguments"
                                            ),
                                            type="AssertionError",
                                            text=(
                                                "AssertionError: expected processAccountDeletionInRange to "
                                                "be called once and with exact arguments"
                                            ),
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    MochaJUnitXmlTestSuites(
                        name="Mocha Tests",
                        tests=1,
                        failures=0,
                        time=0.001,
                        test_suites=[
                            MochaJUnitXmlTestSuite(
                                name="quickDelete",
                                timestamp="2024-07-19T00:18:13",
                                tests=1,
                                failures=0,
                                file=(
                                    "/home/circleci/project/packages/fxa-auth-server/test/local/"
                                    "account-delete.js"
                                ),
                                time=0.001,
                                test_cases=[
                                    MochaJUnitXmlTestCase(
                                        name="AccountDeleteManager quickDelete should delete the account",
                                        classname="should delete the account",
                                        time=0.001,
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
]

EXPECTED_NEXTEST = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-08-21T23:36:28Z",
                test_suites=[
                    NextestJUnitXmlTestSuites(
                        name="autopush-unit-tests",
                        tests=1,
                        failures=0,
                        errors=0,
                        time=4.287,
                        timestamp="2024-08-21T23:36:28.658+00:00",
                        uuid="4ded7634-4e81-40ac-b3f9-060ffa546238",
                        test_suites=[
                            NextestJUnitXmlTestSuite(
                                name="autoendpoint::bin/autoendpoint",
                                tests=1,
                                failures=0,
                                skipped=0,
                                errors=0,
                                test_cases=[
                                    NextestJUnitXmlTestCase(
                                        name="error::tests::sentry_event_with_extras",
                                        classname="autoendpoint::bin/autoendpoint",
                                        timestamp="2024-08-21T23:36:36.475+00:00",
                                        time=4.287,
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )
]

EXPECTED_PLAYWRIGHT = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-07-17T00:23:12Z",
                test_suites=[
                    PlaywrightJUnitXmlTestSuites(
                        id="",
                        name="",
                        tests=1,
                        failures=1,
                        skipped=0,
                        errors=0,
                        time=26.845,
                        test_suites=[
                            PlaywrightJUnitXmlTestSuite(
                                name="react-conversion/oauthSignin.spec.ts",
                                timestamp="2024-07-17T00:23:12.353Z",
                                hostname="local",
                                tests=1,
                                failures=1,
                                skipped=0,
                                time=26.845,
                                errors=0,
                                test_cases=[
                                    PlaywrightJUnitXmlTestCase(
                                        name=(
                                            "react OAuth signin › verified account with cached login, no "
                                            "email confirmation required"
                                        ),
                                        classname="react-conversion/oauthSignin.spec.ts",
                                        time=26.845,
                                        failure=PlaywrightJUnitXmlFailure(
                                            message=(
                                                "oauthSignin.spec.ts:41:9 verified account with cached"
                                                " login, no email confirmation required"
                                            ),
                                            type="FAILURE",
                                            text="Error: page.goto: NS_BINDING_ABORTED",
                                        ),
                                        system_out=(
                                            "[[ATTACHMENT|../functional/react-conversion-oauthSign-"
                                            "916d9-email-confirmation-required-local/trace.zip]]"
                                            "[[ATTACHMENT|../functional/react-conversion-oauthSign-"
                                            "916d9-email-confirmation-required-local-retry1/trace.zip]]"
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PlaywrightJUnitXmlTestSuites(
                        id="",
                        name="",
                        tests=1,
                        failures=0,
                        skipped=1,
                        errors=0,
                        time=8.756,
                        test_suites=[
                            PlaywrightJUnitXmlTestSuite(
                                name="syncV3/signinCached.spec.ts",
                                timestamp="2024-04-07T00:18:43.341Z",
                                hostname="local",
                                tests=1,
                                failures=0,
                                skipped=1,
                                time=8.756,
                                errors=0,
                                test_cases=[
                                    PlaywrightJUnitXmlTestCase(
                                        name=(
                                            "sync signin cached › sign in on desktop then specify a "
                                            "different email on query parameter continues to cache desktop "
                                            "signin"
                                        ),
                                        classname="syncV3/signinCached.spec.ts",
                                        time=8.756,
                                        properties=PlaywrightJUnitXmlProperties(
                                            property=[
                                                PlaywrightJUnitXmlProperty(
                                                    name="fixme",
                                                    value="test to be fixed, see FXA-9194",
                                                )
                                            ]
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PlaywrightJUnitXmlTestSuites(
                        id="",
                        name="",
                        tests=1,
                        failures=0,
                        skipped=0,
                        errors=0,
                        time=1148.7179780000001,
                        test_suites=[
                            PlaywrightJUnitXmlTestSuite(
                                name="settings/changeEmailBlocked.spec.ts",
                                timestamp="2024-08-03T00:22:46.165Z",
                                hostname="local",
                                tests=1,
                                failures=0,
                                skipped=0,
                                time=28.136,
                                errors=0,
                                test_cases=[
                                    PlaywrightJUnitXmlTestCase(
                                        name=(
                                            "change primary - unblock › change primary email, get blocked "
                                            "with invalid password, redirect enter password page"
                                        ),
                                        classname="settings/changeEmailBlocked.spec.ts",
                                        time=28.136,
                                        system_out=(
                                            "[[ATTACHMENT|../functional/settings-changeEmailBlocke-"
                                            "81857-edirect-enter-password-page-local/trace.zip]]"
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PlaywrightJUnitXmlTestSuites(
                        id="",
                        name="",
                        tests=1,
                        failures=0,
                        skipped=1,
                        errors=0,
                        time=5.577,
                        test_suites=[
                            PlaywrightJUnitXmlTestSuite(
                                name="misc/forceAuth.spec.ts",
                                timestamp="2024-05-15T14:25:27.188Z",
                                hostname="production",
                                tests=1,
                                failures=0,
                                skipped=1,
                                time=5.577,
                                errors=0,
                                test_cases=[
                                    PlaywrightJUnitXmlTestCase(
                                        name="force auth › with a registered email, registered uid",
                                        classname="misc/forceAuth.spec.ts",
                                        time=5.577,
                                        properties=PlaywrightJUnitXmlProperties(
                                            property=[
                                                PlaywrightJUnitXmlProperty(
                                                    name="skip",
                                                    value="FXA-8267",
                                                )
                                            ]
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PlaywrightJUnitXmlTestSuites(
                        id="",
                        name="",
                        tests=1,
                        failures=0,
                        skipped=0,
                        errors=0,
                        time=21.957,
                        test_suites=[
                            PlaywrightJUnitXmlTestSuite(
                                name="key-stretching-v2/totp.spec.ts",
                                timestamp="2024-07-17T00:22:53.711Z",
                                hostname="local",
                                tests=1,
                                failures=0,
                                skipped=0,
                                time=21.957,
                                errors=0,
                                test_cases=[
                                    PlaywrightJUnitXmlTestCase(
                                        name="signs up as v1, enable totp, signs in as v2",
                                        classname="key-stretching-v2/totp.spec.ts",
                                        time=21.957,
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        ],
    )
]

EXPECTED_PYTEST = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-07-03T15:05:24Z",
                test_suites=[
                    PytestJUnitXmlTestSuites(
                        test_suites=[
                            PytestJUnitXmlTestSuite(
                                name="pytest",
                                timestamp="2024-07-03T15:05:24.279183",
                                hostname="ip-10-0-175-52",
                                tests=1,
                                failures=1,
                                skipped=0,
                                time=0.019,
                                errors=0,
                                test_cases=[
                                    PytestJUnitXmlTestCase(
                                        name="test_get_weather_report_from_cache_without_ttl",
                                        classname=(
                                            "tests.integration.providers.weather.backends.test_accuweather"
                                        ),
                                        time=0.019,
                                        failure=PytestJUnitXmlFailure(
                                            message="AssertionError",
                                            text="AssertionError",
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PytestJUnitXmlTestSuites(
                        test_suites=[
                            PytestJUnitXmlTestSuite(
                                name="pytest",
                                timestamp="2024-08-06T09:17:36.201378",
                                hostname="ip-10-0-175-52",
                                tests=1,
                                failures=0,
                                skipped=1,
                                time=0.0,
                                errors=0,
                                test_cases=[
                                    PytestJUnitXmlTestCase(
                                        name="test_enabled_by_default",
                                        classname="tests.unit.providers.weather.test_provider",
                                        time=0.0,
                                        skipped=PytestJUnitXmlSkipped(
                                            type="pytest.skip",
                                            message="see DISCO-5555",
                                            text=(
                                                "/merino-py/tests/unit/providers/weather/"
                                                "test_provider.py:59:\n                see DISCO-5555"
                                            ),
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    PytestJUnitXmlTestSuites(
                        test_suites=[
                            PytestJUnitXmlTestSuite(
                                name="pytest",
                                timestamp="2024-07-03T15:05:24.279183",
                                hostname="ip-10-0-175-52",
                                tests=1,
                                failures=0,
                                skipped=0,
                                time=0.178,
                                errors=0,
                                test_cases=[
                                    PytestJUnitXmlTestCase(
                                        name="test_unknown_providers_should_shutdown_app",
                                        classname="tests.integration.test_setup",
                                        time=0.178,
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        ],
    )
]

EXPECTED_TAP = [
    JUnitXmlGroup(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        junit_xmls=[
            JUnitXmlJobTestSuites(
                job=1,
                job_timestamp="2024-01-01T00:00:00Z",
                test_suites=[
                    TapJUnitXmlTestSuites(
                        test_suites=[
                            TapJUnitXmlTestSuite(
                                name="Subtest: test/local/ban_tests.js",
                                tests=1,
                                failures=0,
                                errors=0,
                                test_cases=[
                                    TapJUnitXmlTestCase(
                                        name="#1 test/local/ban_tests.js",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )
]


@pytest.mark.parametrize(
    "artifact_directory, expected_results",
    [
        ("xml_samples_jest", EXPECTED_JEST),
        ("xml_samples_mocha", EXPECTED_MOCHA),
        ("xml_samples_nextest", EXPECTED_NEXTEST),
        ("xml_samples_playwright", EXPECTED_PLAYWRIGHT),
        ("xml_samples_pytest", EXPECTED_PYTEST),
        ("xml_samples_tap", EXPECTED_TAP),
    ],
    ids=["jest", "mocha", "nextest", "playwright", "pytest", "tap"],
)
def test_parse(
    test_data_directory: Path, artifact_directory: str, expected_results: list[JUnitXmlGroup]
) -> None:
    """Test JUnitXmlParser parse method with various test data.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        artifact_directory (str): Test data directory name.
        expected_results (list[SuiteReporterResult]): Expected results from the JUnitXmlParser.
    """
    artifact_path: Path = test_data_directory / artifact_directory
    artifact_file_path: list[Path] = sorted([file_path for file_path in artifact_path.iterdir()])
    parser = JUnitXmlParser()

    actual_results: list[JUnitXmlGroup] = parser.parse(artifact_file_path)

    assert actual_results == expected_results
