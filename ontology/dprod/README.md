# DPROD - Ontology for Data Product Descriptions

This folder contains the Ontology for Data Product Descriptions according to data mesh principles. It is mainly based on the [Data Product Descriptor Specification](https://dpds.opendatamesh.org/resources/specifications/1.0.0-DRAFT/)

## File Overview

- [dprod-ontology.ttl](dprod-ontology.ttl): classes and properties definitions (new terms)
- [dprod-dcatprofile.ttl](dprod-dcatprofile.ttl): shacl shapes file for using DPROD to describe data products (data model)


## Executing the Ontology Pipeline

### Requirements

To execute the ontology pipeline you need:
- [Task](https://taskfile.dev/)
- [Docker](https://www.docker.com/), [Podman](https://podman.io/), or a compatible container engine
- [Python 3](https://www.python.org/)

Further documentation of the ontology pipeline is available at https://github.com/eccenca/ontology-pipeline-template .

### Build Artifacts

The build artifacts are generated in the directory `artifacts`. In the GitHub Action Workflow the artifacts are attached to a successful build (not integrated to this repository yet).

### Building the Documentation and Running RDFUnit Tests

To build documentation for the terms defined in `dprod.ttl` and run [rdfunit-tests](https://github.com/AKSW/RDFUnit) you can use the following commands:

```
task pipeline:validation #run rdfunit tasks

task pipeline:artifacts  #generate documentation
```

### Pipeline Artifacts
- The Ontology Documentation:
  - `schema-documentation.html`
- The RDFUnit test results:
  - `check-rdfunit-auto-results.html`
  - `check-rdfunit-auto-results.xml`
  - `check-rdfunit-manual-results.html`
  - `check-rdfunit-manual-results.xml`
 
### TODO for using the pipeline with eccenca CMEM

- [ ] 🛠️ Adjust config in `cmemc.ini` (Find details on [documentation.eccenca.com](https://documentation.eccenca.com/latest/automate/cmemc-command-line-interface/configuration/file-based-configuration/))
- [ ] 📡 Make sure to setup a remote for `git push`
- [ ] 🔗 Create a `prefixes.ttl`
- [ ] 📑 Make sure `dprod.ttl`, `dprod.nt`, and `dprod.nt.graph` exist
- [ ] 📝 Make sure `dprod-sh.ttl`, `dprod-sh.nt`, and `dprod-sh.nt.graph` exist
- [ ] 💾 Commit the newly created files


