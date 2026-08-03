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
- **Issue branches** &mdash; Created from `develop` for exactly one GitHub
  issue. Use `issue/<number>-<slug>` for GitHub-only work (for example,
  `issue/213-github-issues-source-of-truth`) or the OMG JIRA issue number
  when one exists (for example, `DPROD-16`).
- **Ballot branches** &mdash; Created by the ballot administrator
  to group issue branches for a formal vote (e.g., `ballot/3`).

## 1. Issue Branches

- **Create a branch**: For every issue you work on, create a dedicated
  branch from `develop` using the naming convention above.
- **Isolate changes**: Only commit changes related to the specific issue
  on that branch. Keep commits concise and focused.
- **Open a pull request**: Open a draft pull request early, link the
  GitHub issue, and keep the branch and pull request limited to that
  issue. Mark it ready only after its regression tests pass and the
  issue's acceptance criteria are satisfied.
- **Do not use branches as backlogs**: A long-lived branch must not
  accumulate unrelated pending decisions or work items. Split them into
  GitHub issues and issue branches instead.

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

- **Canonical backlog**: GitHub Issues is the canonical and exclusive backlog for all outstanding DPROD work and design decisions. Do not maintain issue lists, status tables, execution plans, or decision queues in repository Markdown files or branches. Put rationale, alternatives, acceptance criteria, and reviewer discussion on the relevant issue.
- **Commit messages**: Write clear and informative commit messages that
  explain *why* the change was made, not just what changed.
- **Issue tracking**: Keep the
  [GitHub issue](https://github.com/EKGF/dprod/issues) updated with work
  status and link every pull request to it. When an
  [OMG JIRA](https://issues.omg.org/browse/DPROD) item exists, reference
  its identifier in the GitHub issue, branch, and commit messages rather
  than maintaining a second backlog in repository files.
- **Cleanup**: Delete merged, superseded, or abandoned branches after
  verifying that they contain no unique work. Close duplicate or stale
  pull requests with a comment linking the surviving issue or pull
  request.
- **Communication**: Communicate with the ballot administrator and other
  team members throughout the process, especially if you have questions
  or encounter issues.
