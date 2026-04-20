# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

DPROD (Data Product Ontology) is an OMG standard that extends the W3C DCAT vocabulary to describe data products in data mesh architectures. The repository contains the OWL ontology, SHACL validation shapes, a Python spec generator, and worked examples.

## Build

```bash
bash build.sh
```

This sets up a `.venv` with Python 3.12+, installs dependencies, and runs the spec generator. Output goes to `dist/`. The build fetches `https://www.w3.org/ns/dcat2.ttl` remotely, so it requires internet access.

To run just the generator (after initial setup):

```bash
source .venv/bin/activate
python spec-generator/main.py
```

There are no tests or linters configured.

## Architecture

### Spec Generation Pipeline

The spec generator (`spec-generator/main.py`) produces the specification HTML and serialized ontology files:

1. **Load** — Three RDF sources are parsed into a single graph: `dprod-ontology.ttl` (OWL classes/properties), `dprod-shapes.ttl` (SHACL shapes), and the remote W3C DCAT vocabulary.
2. **Discover** — The graph is scanned for SHACL NodeShapes. Each NodeShape is linked to its OWL target class via `sh:targetClass`. Properties come from `sh:property` on each NodeShape.
3. **Two-pass property loading** — For both NodeShapes and PropertyShapes, OWL properties are loaded first, then SHACL properties override them. Predicates in `IGNORED_NODE_SHAPE_PREDICATES` / `IGNORED_PROPERTY_SHAPE_PREDICATES` (in `globals.py`) are skipped during the SHACL pass to prevent shape metadata from leaking into the spec.
4. **Examples** — Each subdirectory in `examples/` with a `README.md` is loaded; the markdown is converted to HTML.
5. **Render** — Jinja2 renders `respec/template.html` with the discovered classes and examples, producing `dist/index.html`.
6. **Serialize** — The ontology is serialized to Turtle, JSON-LD, and RDF/XML in multiple combinations (ontology-only, shapes-only, combined). A standalone `dprod-context.jsonld` is also generated for use as a remote `@context` in JSON-LD documents.

### Key relationships

- `dprod-ontology.ttl` defines OWL classes and properties (the "what").
- `dprod-shapes.ttl` defines SHACL shapes that constrain those classes (the "how to validate"). Each NodeShape targets an OWL class; each PropertyShape constrains an OWL property via `sh:path`.
- `respec/template.html` is both a W3C ReSpec document and a Jinja2 template. Static sections (preamble, scope, namespaces) are plain HTML. Dynamic sections use `{% for cls in classes %}` loops to render class and property tables.
- Class ordering in the spec is hardcoded in `main.py` (the `reorder_list` call), not derived from the ontology.
- Examples referenced in `@context` use `dprod-context.jsonld` (standalone context), not `dprod.jsonld` (full ontology dump).

### Namespace

The canonical namespace is `https://www.omg.org/spec/DPROD/`. The shapes namespace is `https://www.omg.org/spec/DPROD/shapes/`. These are defined in `globals.py`.

## Branch Model and Git Workflow

- **`main`** — The officially accepted OMG standard. Deploys to GitHub Pages.
- **`develop`** — Working branch where the EKGF evolves the standard.
- **Issue branches** — Created from `develop`, named after the OMG JIRA issue number (e.g., `DPROD-16`). Commit messages should reference both the JIRA issue and the GitHub issue (e.g., `Resolves: DPROD-16, #29`).
- **Ballot branches** — Named `ballot/N` (e.g., `ballot/3`), created by the ballot administrator to group issue branches for a formal OMG vote. Merged into `develop` with a merge commit (not squash/rebase) to preserve individual issue history.

See `CONTRIBUTING.md` for the full process.

## Common Modifications

- **Add/modify an ontology class or property**: Edit both `ontology/dprod/dprod-ontology.ttl` (OWL definition) and `ontology/dprod/dprod-shapes.ttl` (SHACL shape). Keep descriptions in sync.
- **Change spec rendering or layout**: Edit `respec/template.html`. Static content is plain HTML; dynamic content uses Jinja2 syntax.
- **Change class ordering in the spec**: Edit the `reorder_list` call in `spec-generator/main.py`.
- **Add an example**: Create a subdirectory in `examples/` with a `README.md` (and optionally an `example.jsonld`). Update `examples/README.md`.
- **Add a namespace to the spec**: Add a `<tr>` to the namespace table in `respec/template.html` and ensure the prefix is declared in the relevant `.ttl` files.
