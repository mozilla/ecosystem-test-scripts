# TestRail Metric Interpretation Guide

This document helps explain the TestRail test case metrics dashboard. This dashboard is to help track the overall trend of test case automation within a project and to help identify potential test cases that are suitable for automation.

## Test Case Automation Statuses

There are 5 Automation Statuses that a test case can have: Suitable, Completed, Disabled, Unsuitable and Untriaged.

**Suitable**

This test case is suitable and can be prioritized for automation. These cases have been evaluated by Test Engineering, SoftVision or project engineers are automatable.

**Completed**

This test case has been automated successfully and has been reviewed by the interested parties as well as Test Engineering.

**Disabled**

This test case is disabled from both manual and automated test runs. These should be reviewed periodically by the engineering team to evaluate if it can be moved out of the Disabled status.

**Unsuitable**

This test case cannot be automated due to its complex nature. These should be reviewed periodically by the engineering team to evaluate if it can be moved out of the Unsuitable status.

**Untriaged**

This test case has not been evaluated for automation. This is the default status for test cases added to TestRail and should be reviewed as soon as possible.

## Automation Status Trend

This view tracks the trend that test cases get updated on TestRail. As test cases are marked with an automation status
that matches one of the above, this will show up on this view. This gives an overview of how the automation work for the tracked test suites is progressing over time.

## Test Case Coverage

This view tracks the overall percentages of the 5 statuses listed above.
