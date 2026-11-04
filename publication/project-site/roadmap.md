---
title: "Roadmap"
description: "Where DPROD came from, what's in flight today, and how the OMG ballot process shapes the evolution of the standard."
permalink: /roadmap/
nav_order: 5
grapharch:
  subject: urn:dprod:project-site:page:roadmap
  fragment: urn:dprod:content:roadmap
---

Work in progress

# Roadmap

DPROD evolves through formal OMG ballots. Here is where it has been, where it is now, and how the process works.

## Timeline

1. Done — 2024

   ### DPROD 1.0 published for public comment

   OMG released the DPROD proposed specification as part of its standardisation process. The 1.0 version is frozen and serves as the official reference point.
2. Done — 2024

   ### OMG Request for Comments completed

   Community feedback gathered through the OMG RFC cycle informed a backlog of improvements now being addressed in subsequent ballots.
3. In progress — Ballot 4

   ### Modelling and clarity improvements

   Fixes to class identifiers in the generated spec, protocol modelling, lifecycle status values, SHACL shape hygiene, and worked examples for data rights. Approved individual issues are bundled for a single vote.
4. Planned — Later ballots

   ### Deeper alignment and new examples

   More worked examples, tighter alignment with neighbouring OMG and W3C vocabularies, and tooling improvements. Priorities are set by the working group and driven by community issues.

## How the OMG ballot process works

### Issues become branches

Every improvement is tracked as an OMG JIRA issue and implemented on its own Git branch named after the issue (e.g. `DPROD-21`). This keeps individual changes reviewable in isolation.

### Issue branches land on `develop`

Once an issue is approved by the working group, the branch is merged into `develop`. The `develop` branch always reflects the current working draft of the standard.

### Ballots bundle issues for a formal vote

When enough issues are ready, a ballot branch (e.g. `ballot/4`) gathers them for a single OMG vote. Bundling preserves individual issue history while giving the membership one thing to vote on.

### Approved ballots update the standard

A passing ballot merges into the canonical branch and the bundled changes become part of the next official version of DPROD.

This page is intentionally a placeholder for the phase-1 site. A more detailed roadmap, with linked issues and target versions, will replace it once the working group signs off on the public milestones.
