# Contribution Guidelines

Anyone is welcome to contribute to this project. Feel free to get in touch with other community
members on [Matrix][1], the mailing list or through issues here on GitHub.

## Code of Conduct

You must agree to abide by the [Mozilla Community Participation Guidelines][2]

## Bug Reports

You can file issues here on GitHub. Please try to include as much information as you can and under
what conditions you saw the issue.

## Sending Pull Requests

Patches should be submitted as pull requests (PR).

Before submitting a PR:

- Ensure you are pulling from the most recent `main` branch.
- Your code must run and pass all the automated tests before you submit your PR for review.
  "Work in progress" or "Draft" pull requests are allowed to be submitted, but should be clearly
  labeled as such and  should not be merged until all tests pass and the code has been reviewed.
- Your patch should include new tests that cover your changes. It is your and your reviewer's
  responsibility to ensure your patch includes adequate tests.

When submitting a PR:

- You agree to license your code under the project's open source license ([MPL 2.0](/LICENSE)).
- Base your branch off the current `main`.
- Add both your code and new tests if relevant.
- Your patch must be [signed][3] to ensure the commits come from a trusted source.
- Run tests, linting and formatting checks to make sure your code complies with established 
  standards.
- Ensure your changes do not reduce code coverage of the test suite.
- Please do not include merge commits in pull requests; include only commits
  with the new relevant code.

## Code Review

This project is subject to our [committing rules and responsibilities][4]. Every patch must be peer
reviewed.

## Git Commit Guidelines & Branch Naming

We loosely follow the [Angular commit guidelines][5] of `<type>: <subject>` where `type` must be one
of:

* **feat**: A new feature
* **fix**: A bug fix
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing
  semi-colons, etc)
* **refactor**: A code change that neither fixes a bug or adds a feature
* **perf**: A code change that improves performance
* **test**: Adding missing tests, test maintenance, and adding test features
* **chore**: Changes to the build process or auxiliary tools and libraries such as documentation
  generation

### Scope

The scope could be anything specifying place of the commit change. For example `circleci`, `github`,
`junit` etc...

### Subject

The subject contains succinct description of the change:

* use the imperative, present tense: "change" not "changed" nor "changes"
* don't capitalize first letter
* no dot (.) at the end

### Body

You can write a detailed description of the commit: Just as in the
**subject**, use the imperative, present tense: "change" not "changed" nor
"changes" It should include the motivation for the change and contrast this with
previous behavior.

### Footer

The footer should contain any information about **Breaking Changes** and is also the place to
reference the JIRA or GitHub issues that this commit relates to. In order to maintain a reference
to the context of the commit, add `Closes #<issue_number>` if it closes a related issue or
`Issue #<issue_number>` if it's a partial implementation.

### Example

A properly formatted commit message should look like:

```
feat(cookie-provider): give the developers a delicious cookie

This patch will provide a delicious cookie when all tests have passed and the commit message is
properly formatted.

BREAKING CHANGE: This patch requires developer to lower expectations about what "delicious" and
"cookie" may mean. Some sadness may result.

Closes #314, Closes #975
```

[1]: https://chat.mozilla.org
[2]: https://www.mozilla.org/about/governance/policies/participation/
[3]: https://help.github.com/articles/managing-commit-signature-verification
[4]: https://firefox-source-docs.mozilla.org/contributing/
[5]: https://github.com/angular/angular/blob/main/CONTRIBUTING.md