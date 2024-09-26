# Metric Interpretation Guide

The purpose of this document is to help individuals understand and interpret the metrics that
represent the health of their test suites and ensure that tests contribute to rapid development and
high product quality. Test metrics provide insights into test performance, helping teams address
potential issues early and monitor improvement efforts. While these metrics offer valuable data
about the health of test suites, they do not necessarily measure the effectiveness of the test cases
themselves.

## Test Suite Size & Success Rates

_Supported Test Frameworks:_ [jest][1], [mocha][2], [nextest][3], [playwright][4], [pytest][5], [tap][6]\
_Supported CI:_ [CircleCI][7]

**Test Suite Size**

Test suite size refers to the number of tests in a suite and serves as a control measure.
Unexplained changes, such as sudden growth or shrinkage, may indicate test runner issues or attempts
to manipulate the scope or quality of the suite. Test suite size should correspond to the state of
the product. For example, a product under active development should show a gradual increase in the
size of its test suite, while a product in maintenance should exhibit more stable trends.

**Success Rates**

Success rates provide a quick indication of the test suite's health. A low success rate or high
failure rate signals potential quality issues, either in the product or within the test suite
itself. This metric can be tracked on both a test-by-test basis and for the entire test suite.

**Average Success Rates**

To avoid noise from isolated failures and spot trends more easily, it's helpful to calculate
averaged success rates over time. This allows teams to act early if trends toward failure begin to
emerge, preventing the test suite from becoming unreliable or mistrusted. Success rate averages are
calculated as:

```text
100 x (Successful Runs / (All Runs - Cancelled Runs))
```

These averages can be calculated over 30-day, 60-day, and 90-day periods, with the 90-day trend
being preferred. Average success rates are typically interpreted as follows, though teams may adjust
thresholds based on their specific needs:

| Threshold | Interpretation                                                     |
|-----------|--------------------------------------------------------------------|
| \>= 95%   | Healthy - Tests pass the majority of the time                      |
| 90% - 95% | Caution - Tests show signs of instability, requiring investigation |
| < 90%     | Critical - Tests are faulty and need intervention                  |

## Time Measurements

_Supported Test Frameworks:_ [jest][1], [mocha][2], [nextest][3], [playwright][4], [pytest][5]\
_Supported CI:_ [CircleCI][7]

Time measurements track how long it takes for tests to run. Ideally, these times should be
proportional to the size of the test suite and remain stable over time. Significant increases or
variations in execution time may indicate performance issues or inefficiencies within the test
suite. Monitoring execution times allows teams to identify and address bottlenecks to keep test
suites efficient.

**Run Time**

The cumulative time of all test runs in a suite.

**Execution Time**

The total time taken for the test suite to execute. If tests are not run in parallel, the execution
time should match the run time.

**Job Time**

The time taken for the test job to complete in CI. Job time thresholds are typically interpreted as
follows:

| Threshold | Interpretation                                             |
|-----------|------------------------------------------------------------|
| \> 10m    | Slow - The test suite may require optimization             |
| <= 10m    | Fast - The test suite runs within an acceptable time frame |

## Coverage Metrics

_Supported Coverage Frameworks:_ [pytest-cov][8], [llvm-cov][9]

Coverage metrics measure the percentage of the codebase covered by tests. They help identify
untested areas of the code, allowing teams to determine whether critical paths are adequately
covered.

While high coverage percentages are generally good, they don’t always guarantee that the tests are
meaningful. The quality and relevance of tests should be balanced with coverage goals. The following
thresholds for line coverage provide general guidance but can be adjusted according to project
needs:

| Threshold | Interpretation                                                                                                                                                              |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| \>= 95%   | High - Potential for metric gaming or diminishing returns.<br/> _* For teams using pytest-cov, the `line excluded` measure may offer further insight into coverage gaming._ |
| 80% - 95% | Good - Suitable for high-risk or high-incident projects                                                                                                                     |
| 60% - 79% | Acceptable - Suitable for low-risk or low-incident projects                                                                                                                 |
| < 60%     | Low - Coverage should be improved                                                                                                                                           |

## Skip Rates

_Supported Test Frameworks:_ [jest][1], [mocha][2], [nextest][3], [playwright][4], [pytest][5]\
_Supported CI:_ [CircleCI][7]

Skip rates indicate how often tests are temporarily excluded from execution. While skipping tests
can be a necessary short-term solution to prevent flaky tests from disrupting workflows, high or
sustained skip rates can signal deeper issues with the test suite's sustainability.

Long-term skips may indicate that tests have fallen into disrepair, and an increasing skip rate
can point to team capacity or prioritization problems. Monitoring skip rates ensures that skipped
tests are revisited and resolved promptly. Thresholds for skip rates are typically interpreted as
follows:

| Threshold | Interpretation                                                                        |
|-----------|---------------------------------------------------------------------------------------|
| \> 2%     | Critical - Test coverage is compromised, requiring immediate intervention             |
| 1% - 2%   | Caution - Test coverage is at risk, and the suite may become prone to silent failures |
| <= 1%     | Healthy - Most of the test suite is running, ensuring comprehensive coverage          |

Note: Playwright offers both `skipme` and `fixme` annotations, allowing for further refinement of
this metric.

## Retry Rates

_Supported Test Frameworks:_ [playwright][4]

Retry rates track how often tests are re-executed following a failure. While retries can help
address transient issues, such as network errors, elevated retry rates may indicate flakiness in the
test suite or performance regressions in the product. High retry rates can increase execution times
and negatively impact developer workflows. Monitoring retry rates helps teams identify and fix
unstable tests, ensuring predictable test execution.

[1]: https://jestjs.io/
[2]: https://mochajs.org/
[3]: https://nexte.st/
[4]: https://playwright.dev/
[5]: https://docs.pytest.org/
[6]: https://node-tap.org/
[7]: https://circleci.com/
[8]: https://pypi.org/project/pytest-cov/
[9]: https://llvm.org/docs/CommandGuide/llvm-cov.html
