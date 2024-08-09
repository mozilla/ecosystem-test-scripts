# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the JUnitXmlParser module."""

from pathlib import Path

import pytest

from scripts.metric_reporter.junit_xml_parser import (
    JUnitXMLFailure,
    JUnitXMLJobTestSuites,
    JUnitXmlParser,
    JUnitXMLProperty,
    JUnitXMLSkipped,
    JUnitXMLSystemOut,
    JUnitXMLTestCase,
    JUnitXMLTestSuite,
    JUnitXMLTestSuites,
)

EXPECTED_JEST = [
    JUnitXMLJobTestSuites(
        job=1,
        test_suites=[
            JUnitXMLTestSuites(
                id=None,
                name="jest tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=0,
                time=0.0,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="#integration - FirestoreService",
                        timestamp="2024-05-18T00:21:34",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=0.0,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="#integration - FirestoreService should be defined",
                                classname="#integration - FirestoreService should be defined",
                                time=0.0,
                                properties=None,
                                skipped=JUnitXMLSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id=None,
                name="jest tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=0,
                time=0.042,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="lib/amplitude",
                        timestamp="2024-07-19T00:18:01",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=0.042,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
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
    JUnitXMLJobTestSuites(
        job=1,
        test_suites=[
            JUnitXMLTestSuites(
                id=None,
                name="Mocha Tests",
                tests=1,
                failures=1,
                skipped=None,
                errors=None,
                time=0.002,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="deleteUnverifiedAccounts",
                        timestamp="2024-07-19T00:18:31",
                        hostname=None,
                        tests=1,
                        failures=1,
                        skipped=None,
                        time=0.002,
                        errors=None,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="CloudSchedulerHandler deleteUnverifiedAccounts should call processAccountDeletionInRange with correct parameters",
                                classname="should call processAccountDeletionInRange with correct parameters",
                                time=0.002,
                                properties=None,
                                skipped=None,
                                failure=JUnitXMLFailure(
                                    message="expected processAccountDeletionInRange to be called once and with exact arguments",
                                    type="AssertionError",
                                    text="\n                AssertionError: expected processAccountDeletionInRange to be called once and with exact arguments\n            ",
                                ),
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id=None,
                name="Mocha Tests",
                tests=1,
                failures=0,
                skipped=None,
                errors=None,
                time=0.001,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="quickDelete",
                        timestamp="2024-07-19T00:18:13",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=None,
                        time=0.001,
                        errors=None,
                        test_cases=[
                            JUnitXMLTestCase(
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
    JUnitXMLJobTestSuites(
        job=1,
        test_suites=[
            JUnitXMLTestSuites(
                id="",
                name="",
                tests=1,
                failures=1,
                skipped=0,
                errors=0,
                time=26.845,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="react-conversion/oauthSignin.spec.ts",
                        timestamp="2024-07-17T00:23:12.353Z",
                        hostname="local",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=26.845,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="severity-1 #smoke › react OAuth signin › verified account with cached login, no email confirmation required",
                                classname="react-conversion/oauthSignin.spec.ts",
                                time=26.845,
                                properties=None,
                                skipped=None,
                                failure=JUnitXMLFailure(
                                    message="oauthSignin.spec.ts:41:9 verified account with cached login, no email confirmation required",
                                    type="FAILURE",
                                    text='\n                  [local] › react-conversion/oauthSignin.spec.ts:41:9 › severity-1 #smoke › react OAuth signin › verified account with cached login, no email confirmation required\n\n    Error: page.goto: NS_BINDING_ABORTED\n    Call log:\n      - navigating to "http://localhost:3030/oauth/signin?showReactApp=true&deviceId=6808fa7211a64d989f06ee4effd55122&flowBeginTime=1721175881860&flowId=a4a02d3d4c6e6496c8794f7ebccdf705e1e0de600fbdc0a7f834f82da01593e0&access_type=offline&client_id=dcdb5ae7add825d2&pkce_client_id=38a6b9b3a65a1871&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fapi%2Foauth&scope=profile%20openid&action=email&state=2ac865bf85dd19a9fe9f8103f60bfb9b4fdc5405308e8a5371c8601a2548835b&flow_id=a4a02d3d4c6e6496c8794f7ebccdf705e1e0de600fbdc0a7f834f82da01593e0&flow_begin_time=1721175881860&device_id=6808fa7211a64d989f06ee4effd55122&email=signind2769b721b66ed80%40restmail.net&forceExperiment=generalizedReactApp&forceExperimentGroup=react", waiting until "load"\n\n\n      68 |\n      69 |       // reload page with React experiment params\n    > 70 |       await page.goto(\n         |                  ^\n      71 |         `${page.url()}&forceExperiment=generalizedReactApp&forceExperimentGroup=react`\n      72 |       );\n      73 |\n\n        at /home/circleci/project/packages/functional-tests/tests/react-conversion/oauthSignin.spec.ts:70:18\n\n    attachment #1: trace (application/zip) ─────────────────────────────────────────────────────────\n    ../../artifacts/functional/react-conversion-oauthSign-916d9-email-confirmation-required-local/trace.zip\n    Usage:\n\n        yarn playwright show-trace ../../artifacts/functional/react-conversion-oauthSign-916d9-email-confirmation-required-local/trace.zip\n\n    ────────────────────────────────────────────────────────────────────────────────────────────────\n\n    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────\n\n    Error: page.goto: NS_BINDING_ABORTED\n    Call log:\n      - navigating to "http://localhost:3030/oauth/signin?showReactApp=true&deviceId=69b8df9d92204f7da1945b309389eb64&flowBeginTime=1721175897833&flowId=aa9a74383215c2645307ad973c338ae79b42696ced8fc0fd7f75b6c899385ddc&access_type=offline&client_id=dcdb5ae7add825d2&pkce_client_id=38a6b9b3a65a1871&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fapi%2Foauth&scope=profile%20openid&action=email&state=49f1f7e4846db5f9d667f959d167878707a1afa1522bee58c96a26357fe2e648&flow_id=aa9a74383215c2645307ad973c338ae79b42696ced8fc0fd7f75b6c899385ddc&flow_begin_time=1721175897833&device_id=69b8df9d92204f7da1945b309389eb64&email=signindf87ef5f15cc792f%40restmail.net&forceExperiment=generalizedReactApp&forceExperimentGroup=react", waiting until "load"\n\n\n      68 |\n      69 |       // reload page with React experiment params\n    > 70 |       await page.goto(\n         |                  ^\n      71 |         `${page.url()}&forceExperiment=generalizedReactApp&forceExperimentGroup=react`\n      72 |       );\n      73 |\n\n        at /home/circleci/project/packages/functional-tests/tests/react-conversion/oauthSignin.spec.ts:70:18\n\n    attachment #1: trace (application/zip) ─────────────────────────────────────────────────────────\n    ../../artifacts/functional/react-conversion-oauthSign-916d9-email-confirmation-required-local-retry1/trace.zip\n    Usage:\n\n        yarn playwright show-trace ../../artifacts/functional/react-conversion-oauthSign-916d9-email-confirmation-required-local-retry1/trace.zip\n\n    ────────────────────────────────────────────────────────────────────────────────────────────────\n\n            ',
                                ),
                                system_out=JUnitXMLSystemOut(
                                    text="\n                \n[[ATTACHMENT|../functional/react-conversion-oauthSign-916d9-email-confirmation-required-local/trace.zip]]\n\n[[ATTACHMENT|../functional/react-conversion-oauthSign-916d9-email-confirmation-required-local-retry1/trace.zip]]\n\n            "
                                ),
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=8.756,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="syncV3/signinCached.spec.ts",
                        timestamp="2024-04-07T00:18:43.341Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=8.756,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="severity-2 #smoke › sync signin cached › sign in on desktop then specify a different email on query parameter continues to cache desktop signin",
                                classname="syncV3/signinCached.spec.ts",
                                time=8.756,
                                properties=[
                                    JUnitXMLProperty(
                                        name="fixme", value="test to be fixed, see FXA-9194"
                                    )
                                ],
                                skipped=JUnitXMLSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=1148.7179780000001,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="settings/changeEmailBlocked.spec.ts",
                        timestamp="2024-08-03T00:22:46.165Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=28.136,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="severity-1 #smoke › change primary - unblock › change primary email, get blocked with invalid password, redirect enter password page",
                                classname="settings/changeEmailBlocked.spec.ts",
                                time=28.136,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=JUnitXMLSystemOut(
                                    text="\n            \n            [[ATTACHMENT|../functional/settings-changeEmailBlocke-81857-edirect-enter-password-page-local/trace.zip]]\n            \n            "
                                ),
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=5.577,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="misc/forceAuth.spec.ts",
                        timestamp="2024-05-15T14:25:27.188Z",
                        hostname="production",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=5.577,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="severity-1 #smoke › force auth › with a registered email, registered uid",
                                classname="misc/forceAuth.spec.ts",
                                time=5.577,
                                properties=[
                                    JUnitXMLProperty(
                                        name="skip",
                                        value="Scheduled for removal as part of React conversion (see FXA-8267).",
                                    )
                                ],
                                skipped=JUnitXMLSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=21.957,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="key-stretching-v2/totp.spec.ts",
                        timestamp="2024-07-17T00:22:53.711Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=21.957,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="severity-2 #smoke › signs up as v1, enable totp, signs in as v2",
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
    JUnitXMLJobTestSuites(
        job=1,
        test_suites=[
            JUnitXMLTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="pytest",
                        timestamp="2024-07-03T15:05:24.279183",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=0.019,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="test_get_weather_report_from_cache_without_ttl",
                                classname="tests.integration.providers.weather.backends.test_accuweather",
                                time=0.019,
                                properties=None,
                                skipped=None,
                                failure=JUnitXMLFailure(
                                    message="AssertionError: assert ['accuweather...it.forecasts'] == ['accuweather...it.forecasts']\n  At index 1 diff: 'accuweather.cache.fetch.miss.ttl' != 'accuweather.cache.hit.currentconditions'\n  Left contains one more item: 'accuweather.cache.hit.forecasts'\n  Full diff:\n    [\n     'accuweather.cache.hit.locations',\n  +  'accuweather.cache.fetch.miss.ttl',\n     'accuweather.cache.hit.currentconditions',\n     'accuweather.cache.hit.forecasts',\n    ]",
                                    type=None,
                                    text='\n                redis_client = Redis<ConnectionPool<Connection<host=localhost,port=32769,db=0>>>\n                geolocation = Location(country=\'US\', country_name=None, region=\'CA\',\n                region_name=None, city=\'San Francisco\', dma=807, postal_code=\'94105\', key=None)\n                statsd_mock = <MagicMock spec=\'Client\' id=\'139764321538688\'>\n                expected_weather_report = WeatherReport(city_name=\'San Francisco\',\n                current_conditions=CurrentConditions(url=Url(\'https://www.accuweather.com/en/.../39376?lang=en-us\'),\n                summary=\'Pleasant Saturday\', high=Temperature(c=21, f=70), low=Temperature(c=14,\n                f=57)), ttl=1800)\n                accuweather_parameters = {\'api_key\': \'test\', \'cached_current_condition_ttl_sec\':\n                1800, \'cached_forecast_ttl_sec\': 1800, \'cached_location_key_ttl_sec\': 1800, ...}\n                accuweather_cached_location_key = b\'{"key": "39376", "localized_name": "San\n                Francisco"}\'\n                accuweather_cached_current_conditions = b\'{"url":\n                "https://www.accuweather.com/en/us/san-francisco-ca/94103/current-weather/39376?lang=en-us",\n                "summary": "Mostly cloudy", "icon_id": 6, "temperature": {"c": 15.5, "f": 60.0}}\'\n                accuweather_cached_forecast_fahrenheit = b\'{"url":\n                "https://www.accuweather.com/en/us/san-francisco-ca/94103/daily-weather-forecast/39376?lang=en-us",\n                "summary": "Pleasant Saturday", "high": {"f": 70.0}, "low": {"f": 57.0}}\'\n\n                @pytest.mark.asyncio\n                async def test_get_weather_report_from_cache_without_ttl(\n                redis_client: Redis,\n                geolocation: Location,\n                statsd_mock: Any,\n                expected_weather_report: WeatherReport,\n                accuweather_parameters: dict[str, Any],\n                accuweather_cached_location_key: bytes,\n                accuweather_cached_current_conditions: bytes,\n                accuweather_cached_forecast_fahrenheit: bytes,\n                ) -> None:\n                """Test that we can get the weather report from cache without a TTL set for forecast\n                and\n                current conditions\n                """\n                # set up the accuweather backend object with the testcontainer redis client\n                accuweather: AccuweatherBackend = AccuweatherBackend(\n                cache=RedisAdapter(redis_client), **accuweather_parameters\n                )\n\n                # get cache keys\n                cache_keys = generate_accuweather_cache_keys(accuweather, geolocation)\n\n                # set the above keys with their values as their corresponding fixtures\n                keys_and_values = [\n                (cache_keys.location_key, accuweather_cached_location_key),\n                (cache_keys.current_conditions_key, accuweather_cached_current_conditions),\n                (cache_keys.forecast_key, accuweather_cached_forecast_fahrenheit),\n                ]\n                await set_redis_keys(redis_client, keys_and_values)\n\n                # this http client mock isn\'t used to make any calls, but we do assert below on it\n                not being\n                # called\n                client_mock: AsyncMock = cast(AsyncMock, accuweather.http_client)\n\n                report: Optional[WeatherReport] = await accuweather.get_weather_report(geolocation)\n\n                assert report == expected_weather_report\n                client_mock.get.assert_not_called()\n\n                metrics_timeit_called = [call_arg[0][0] for call_arg in\n                statsd_mock.timeit.call_args_list]\n                assert metrics_timeit_called == ["accuweather.cache.fetch"]\n\n                metrics_increment_called = [\n                call_arg[0][0] for call_arg in statsd_mock.increment.call_args_list\n                ]\n\n                > assert metrics_increment_called == [\n                "accuweather.cache.hit.locations",\n                "accuweather.cache.hit.currentconditions",\n                "accuweather.cache.hit.forecasts",\n                ]\n                E AssertionError: assert [\'accuweather...it.forecasts\'] ==\n                [\'accuweather...it.forecasts\']\n                E At index 1 diff: \'accuweather.cache.fetch.miss.ttl\' !=\n                \'accuweather.cache.hit.currentconditions\'\n                E Left contains one more item: \'accuweather.cache.hit.forecasts\'\n                E Full diff:\n                E [\n                E \'accuweather.cache.hit.locations\',\n                E + \'accuweather.cache.fetch.miss.ttl\',\n                E \'accuweather.cache.hit.currentconditions\',\n                E \'accuweather.cache.hit.forecasts\',\n                E ]\n\n                tests/integration/providers/weather/backends/test_accuweather.py:456: AssertionError\n            ',
                                ),
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="pytest",
                        timestamp="2024-08-06T09:17:36.201378",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=0.0,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
                                name="test_enabled_by_default",
                                classname="tests.unit.providers.weather.test_provider",
                                time=0.0,
                                properties=None,
                                skipped=JUnitXMLSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            ),
            JUnitXMLTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="pytest",
                        timestamp="2024-07-03T15:05:24.279183",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=0.178,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
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
    JUnitXMLJobTestSuites(
        job=1,
        test_suites=[
            JUnitXMLTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXMLTestSuite(
                        name="Subtest: test/local/ban_tests.js",
                        timestamp=None,
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=None,
                        time=None,
                        errors=0,
                        test_cases=[
                            JUnitXMLTestCase(
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
    expected_results: list[JUnitXMLJobTestSuites],
) -> None:
    """Test JUnitXmlParser parse method with various test data.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        artifact_directory (str): Test data directory name.
        expected_results (list[SuiteReporterResult]): Expected results from the JUnitXmlParser.
    """
    artifact_path = test_data_directory / artifact_directory
    parser = JUnitXmlParser()

    actual_results: list[JUnitXMLJobTestSuites] = parser.parse(artifact_path)

    assert actual_results == expected_results
