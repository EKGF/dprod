It is important to be able to trace the lineage of data. Data Products have input and output ports, and one Data Product’s input port will point to another Data Product’s output port.

This allows a user to query the lineage of where the data has come from by following the inputs. Here is an example query that will return all the input datasets for the finance data product.


```sparql
SELECT DISTINCT ?input
WHERE
{ 
  :company-finance dprod:inputPort ?inputPort.
  ?inputPort dprod:isAccessServiceOf/dprod:isDistributionOf/rdfs:label ?input.
}
```

Based on the data in the example, this query would return:
- Sales
- Payroll


NOTE: If you wish to track lineage at a more granular level, you can also use PROV (https://www.w3.org/TR/prov-o/) at the dataset level. 
See: https://www.w3.org/TR/vocab-dcat-3/#examples-dataset-provenance.
```ttl
dap:atnf-P366-2003SEPT
  rdf:type dcat:Dataset ;
  dcterms:bibliographicCitation "Burgay, M; McLaughlin, M; Kramer, M; Lyne, A; Joshi, B; Pearce, G; D'Amico, N; Possenti, A; Manchester, R; Camilo, F (2017): Parkes observations for project P366 semester 2003SEPT. v1. CSIRO. Data Collection. https://doi.org/10.4225/08/598dc08d07bb7" ;
  dcterms:title "Parkes observations for project P366 semester 2003SEPT"@en ;
  dcat:landingPage <https://data.csiro.au/dap/landingpage?pid=csiro:P366-2003SEPT> ;
  prov:wasGeneratedBy dap:P366 ;
  .

dap:P366
  rdf:type prov:Activity ;
  dcterms:type <http://dbpedia.org/resource/Observation> ;
  prov:startedAtTime "2000-11-01"^^xsd:date ;
  prov:used dap:Parkes-radio-telescope ;
  prov:wasInformedBy dap:ATNF ;
  rdfs:label "P366 - Parkes multibeam high-latitude pulsar survey"@en ;
  rdfs:seeAlso <https://doi.org/10.1111/j.1365-2966.2006.10100.x> ;
  .
```

NOTE: For the example SPARQL query above to run you would also need to include the following prefixes:
  - PREFIX dcat: <http://www.w3.org/ns/dcat#>
  - PREFIX dprod: <https://ekgf.github.io/data-product-spec/dprod/>
  - PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  - PREFIX : <https://y.com/data-product/>
