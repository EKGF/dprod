# GraphArch documentation preview

`grapharch.ttl` declares the HTML reference, companion guide and PDF preview,
and the repository-relative inputs used to build them. It reuses the registered
EKGF authority identity and labels the result as a documentation preview. The
ontology header supplies its title, description, license and publication date.

The preview reads the native ontology and shapes, the repository README and the
existing dataset-schema example. RDF hints supply their website titles and
routes without changing or duplicating their Markdown bodies. `abstract.md` and `status.md`
are authored preview fragments. The existing ReSpec publication process and
normative source RDF are unchanged.

The GraphArch showcase fetches `EKGF/dprod` on `develop` into a bare Git cache,
resolves one commit per build, and collects all these inputs from that same tree.
It does not use copied ontology or narrative files from the GraphArch repository.
Git commit and per-file blob provenance are retained in the documentation KG;
renderers use only the pinned KG.
