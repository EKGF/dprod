# Contributing

This document provides guidelines for contributing to the
[Data Product (DPROD)](https://www.omg.org/spec/DPROD/) specification
using a Git workflow designed for issue-based development and a formal
OMG balloting process.

## Branches

- **`main`** &mdash; The officially accepted OMG standard.
- **`develop`** &mdash; The working branch where the
  [Enterprise Knowledge Graph Forum (EKGF)](https://www.ekgf.org),
  an OMG community, continues to evolve the standard.
- **Issue branches** &mdash; Created from `develop` for each issue,
  named after the OMG JIRA issue number (e.g., `DPROD-16`).
- **Ballot branches** &mdash; Created by the ballot administrator
  to group issue branches for a formal vote (e.g., `ballot/3`).

## 1. Issue Branches

- **Create a branch**: For every issue you work on, create a dedicated
  branch from `develop`. Name it after the OMG JIRA issue number
  (e.g., `DPROD-16`).
- **Isolate changes**: Only commit changes related to the specific issue
  on that branch. Keep commits concise and focused.

## 2. Keeping Your Branch Up-to-Date

- **Rebase from `develop`**: Regularly rebase your issue branch to
  incorporate the latest changes. This helps prevent merge conflicts and
  keeps your branch current.

  ```bash
  git checkout DPROD-16
  git rebase develop
  ```

- **Avoid merging from other branches**: Do not merge changes from other
  issue branches into yours. If absolutely necessary, use squash merging
  to maintain a clean history.

## 3. Ballot Preparation

- **Notification**: You will be notified when your issue is being
  considered for a ballot.
- **Ensure your branch is ready**: Make sure your issue branch is
  up-to-date with `develop` (rebase if needed) and that all commits are
  clear and well-organized.

## 4. Ballot Review

- **Pull request**: The ballot administrator will create a pull request
  for the ballot branch (e.g., `ballot/3`), which includes your issue
  branch.
- **Review**: Review the ballot pull request as a whole or examine your
  individual issue branch to ensure the changes are correct. Provide
  feedback or approvals as needed.

## 5. Post-Ballot

- **Merge to `develop`**: If the ballot passes, the administrator will
  merge the ballot branch into `develop`.
- **Rejected issues**: If your issue is rejected in a ballot:
  - Address the feedback provided.
  - Rebase your branch from `develop` (after the ballot branch is merged).
  - Optionally rename your branch (e.g., add `.1`) to indicate the
    revision.
  - Your issue will be included in a future ballot.

## 6. Important Considerations

- **Commit messages**: Write clear and informative commit messages that
  explain *why* the change was made, not just what changed.
- **Issue tracking**: Keep both
  [GitHub Issues](https://github.com/EKGF/dprod/issues) and
  [OMG JIRA](https://issues.omg.org/browse/DPROD) updated with the
  status of your work. Reference the OMG JIRA issue number in your
  branch name and commit messages (e.g., `DPROD-16`), and reference the
  GitHub issue number where applicable (e.g., `#29`).
- **Communication**: Communicate with the ballot administrator and other
  team members throughout the process, especially if you have questions
  or encounter issues.
