# DPROD PR 234 Schedule model publication

These instructions publish the native main-branch RDF, examples and historical template prose with GraphArch. They do not update the normative ontology, shapes, examples or original template. The date is the ontology’s recorded modification date, not an approval date. Static template prose is mechanically transcribed to Markdown with source hashes recorded in `source-provenance.json`; links now resolve to the authoritative source files or RDF resource IRIs. The existing source diagram is collected unchanged.

Run `python3 -m unittest discover -s publication/tests` to verify preserved sources and publication inputs.
