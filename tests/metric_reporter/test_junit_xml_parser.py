# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the JUnitXmlParser module."""

from pathlib import Path

import pytest

from scripts.metric_reporter.junit_xml_parser import (
    JUnitXmlFailure,
    JUnitXmlJobTestSuites,
    JUnitXmlParser,
    JUnitXmlProperty,
    JUnitXmlSkipped,
    JUnitXmlSystemOut,
    JUnitXmlTestCase,
    JUnitXmlTestSuite,
    JUnitXmlTestSuites,
)

EXPECTED_JEST = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name="jest tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=0,
                time=0.0,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="#integration - FirestoreService",
                        timestamp="2024-05-18T00:21:34",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=0.0,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="#integration - FirestoreService should be defined",
                                classname="#integration - FirestoreService should be defined",
                                time=0.0,
                                properties=None,
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id=None,
                name="jest tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=0,
                time=0.042,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="lib/amplitude",
                        timestamp="2024-07-19T00:18:01",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=0.042,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="lib/amplitude logs a correctly formatted message",
                                classname="lib/amplitude logs a correctly formatted message",
                                time=0.042,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
        ],
    )
]

EXPECTED_MOCHA = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name="Mocha Tests",
                tests=1,
                failures=1,
                skipped=None,
                errors=None,
                time=0.002,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="deleteUnverifiedAccounts",
                        timestamp="2024-07-19T00:18:31",
                        hostname=None,
                        tests=1,
                        failures=1,
                        skipped=None,
                        time=0.002,
                        errors=None,
                        test_cases=[
                            JUnitXmlTestCase(
                                name=(
                                    "CloudSchedulerHandler deleteUnverifiedAccounts should call "
                                    "processAccountDeletionInRange with correct parameters"
                                ),
                                classname=(
                                    "should call processAccountDeletionInRange with correct "
                                    "parameters"
                                ),
                                time=0.002,
                                properties=None,
                                skipped=None,
                                failure=JUnitXmlFailure(
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
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id=None,
                name="Mocha Tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=None,
                time=0.001,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="quickDelete",
                        timestamp="2024-07-19T00:18:13",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=None,
                        time=0.001,
                        errors=None,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="AccountDeleteManager quickDelete should delete the account",
                                classname="should delete the account",
                                time=0.001,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
        ],
    )
]

EXPECTED_PLAYWRIGHT = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=1,
                skipped=0,
                errors=0,
                time=26.845,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="react-conversion/oauthSignin.spec.ts",
                        timestamp="2024-07-17T00:23:12.353Z",
                        hostname="local",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=26.845,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name=(
                                    "react OAuth signin › verified account with cached login, no "
                                    "email confirmation required"
                                ),
                                classname="react-conversion/oauthSignin.spec.ts",
                                time=26.845,
                                properties=None,
                                skipped=None,
                                failure=JUnitXmlFailure(
                                    message=(
                                        "oauthSignin.spec.ts:41:9 verified account with cached"
                                        " login, no email confirmation required"
                                    ),
                                    type="FAILURE",
                                    text="Error: page.goto: NS_BINDING_ABORTED",
                                ),
                                system_out=JUnitXmlSystemOut(
                                    text=(
                                        "[[ATTACHMENT|../functional/react-conversion-oauthSign-"
                                        "916d9-email-confirmation-required-local/trace.zip]]"
                                        "[[ATTACHMENT|../functional/react-conversion-oauthSign-"
                                        "916d9-email-confirmation-required-local-retry1/trace.zip]]"
                                    )
                                ),
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=8.756,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="syncV3/signinCached.spec.ts",
                        timestamp="2024-04-07T00:18:43.341Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=8.756,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name=(
                                    "sync signin cached › sign in on desktop then specify a "
                                    "different email on query parameter continues to cache desktop "
                                    "signin"
                                ),
                                classname="syncV3/signinCached.spec.ts",
                                time=8.756,
                                properties=[
                                    JUnitXmlProperty(
                                        name="fixme", value="test to be fixed, see FXA-9194"
                                    )
                                ],
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=1148.7179780000001,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="settings/changeEmailBlocked.spec.ts",
                        timestamp="2024-08-03T00:22:46.165Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=28.136,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name=(
                                    "change primary - unblock › change primary email, get blocked "
                                    "with invalid password, redirect enter password page"
                                ),
                                classname="settings/changeEmailBlocked.spec.ts",
                                time=28.136,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=JUnitXmlSystemOut(
                                    text=(
                                        "[[ATTACHMENT|../functional/settings-changeEmailBlocke-"
                                        "81857-edirect-enter-password-page-local/trace.zip]]"
                                    ),
                                ),
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=5.577,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="misc/forceAuth.spec.ts",
                        timestamp="2024-05-15T14:25:27.188Z",
                        hostname="production",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=5.577,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="force auth › with a registered email, registered uid",
                                classname="misc/forceAuth.spec.ts",
                                time=5.577,
                                properties=[
                                    JUnitXmlProperty(
                                        name="skip",
                                        value="FXA-8267",
                                    )
                                ],
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=21.957,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="key-stretching-v2/totp.spec.ts",
                        timestamp="2024-07-17T00:22:53.711Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=21.957,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="signs up as v1, enable totp, signs in as v2",
                                classname="key-stretching-v2/totp.spec.ts",
                                time=21.957,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
        ],
    )
]

EXPECTED_PYTEST = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="pytest",
                        timestamp="2024-07-03T15:05:24.279183",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=0.019,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_get_weather_report_from_cache_without_ttl",
                                classname=(
                                    "tests.integration.providers.weather.backends.test_accuweather"
                                ),
                                time=0.019,
                                properties=None,
                                skipped=None,
                                failure=JUnitXmlFailure(
                                    message="AssertionError",
                                    type=None,
                                    text="AssertionError",
                                ),
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="pytest",
                        timestamp="2024-08-06T09:17:36.201378",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=0.0,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_enabled_by_default",
                                classname="tests.unit.providers.weather.test_provider",
                                time=0.0,
                                properties=None,
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXmlTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="pytest",
                        timestamp="2024-07-03T15:05:24.279183",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=0.178,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_unknown_providers_should_shutdown_app",
                                classname="tests.integration.test_setup",
                                time=0.178,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
        ],
    )
]

EXPECTED_TAP = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="Subtest: test/local/ban_tests.js",
                        timestamp=None,
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=None,
                        time=None,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="#1 test/local/ban_tests.js",
                                classname=None,
                                time=None,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
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
        ("xml_samples_playwright", EXPECTED_PLAYWRIGHT),
        ("xml_samples_pytest", EXPECTED_PYTEST),
        ("xml_samples_tap", EXPECTED_TAP),
    ],
    ids=["jest", "mocha", "playwright", "pytest", "tap"],
)
def test_parse(
    test_data_directory: Path,
    artifact_directory: str,
    expected_results: list[JUnitXmlJobTestSuites],
) -> None:
    """Test JUnitXmlParser parse method with various test data.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        artifact_directory (str): Test data directory name.
        expected_results (list[SuiteReporterResult]): Expected results from the JUnitXmlParser.
    """
    artifact_path = test_data_directory / artifact_directory
    parser = JUnitXmlParser()

    actual_results: list[JUnitXmlJobTestSuites] = parser.parse(artifact_path)

    assert actual_results == expected_results
