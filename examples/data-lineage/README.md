It is important to be able to trace the lineage of data. 
Within DPROD, this can be done in two ways: at a high level from one 
data product to another and, if desired, 
at the more detailed level of the underlying datasets.

## High Level Lineage: Between Data Products

Data products have input and output ports, and one data product’s 
input port will point to another data product’s output port.

This allows a user to query the lineage. 
The data products all have URLs as identifiers, and properties all 
connect to each other, so a query can walk from one data product to 
the downstream data products that feed it.

One can follow the path that leads from one data product to
another like this:

```text
Data Product >> inputPort >> isAccessServiceOf >> isDistributionOf >> Input Data Product 
```

The following example data has three data products that 
connect to each other through their input and output ports:

```json
{
  "@context": "https://www.omg.org/spec/DPROD/dprod-context.jsonld",
  "@graph": [
    {
      "@id": "https://y.com/data-product/company-finance",
      "@type": "dprod:DataProduct",
      "dprod:inputPort": [
        {
          "@id": "https://y.com/data-product/company-sales/port/2025-sales",
          "@type": "dcat:DataService"
        },
        {
          "@id": "https://y.com/data-product/company-hr/port/2025-payroll",
          "@type": "dcat:DataService"
        }
      ],
      "dprod:outputPort": {
        "@id": "https://y.com/data-product/company-sales/port/2025-balance-sheet",
        "@type": "dcat:DataService",
        "rdfs:label": "Balance Sheet",
        "dcat:endpointURL": "https://y.com/data-product/company-sales/port/2025-c",
        "dprod:isAccessServiceOf": {
          "@type": "dcat:Distribution",
          "dct:format": "https://www.iana.org/assignments/media-types/application/json",
          "dprod:isDistributionOf": {
            "@id": "https://y.com/data-product/company-sales/dataset/2025-balance-sheet",
            "@type": "dcat:Dataset",
            "dct:conformsTo": "https://y.com/schema/BalanceSheet"
          }
        }
      }
    },
    {
      "@id": "https://y.com/data-product/company-sales",
      "@type": "dprod:DataProduct",
      "dprod:outputPort": {
        "@id": "https://y.com/data-product/company-sales/port/2025-sales",
        "@type": "dcat:DataService",
        "rdfs:label": "Sales",
        "dcat:endpointURL": "https://y.com/data-product/company-sales/port/2025-sales",
        "dprod:isAccessServiceOf": {
          "@type": "dcat:Distribution",
          "dct:format": "https://www.iana.org/assignments/media-types/application/json",
          "dprod:isDistributionOf": {
            "@id": "https://y.com/data-product/company-sales/dataset/2025-sales",
            "@type": "dcat:Dataset",
            "rdfs:label": "Sales",
            "dct:conformsTo": "https://y.com/schema/Sale"
          }
        }
      }
    },
    {
      "@id": "https://y.com/data-product/company-hr",
      "@type": "dprod:DataProduct",
      "dprod:outputPort": {
        "@id": "https://y.com/data-product/company-sales/port/2025-payroll",
        "@type": "dcat:DataService",
        "rdfs:label": "Payroll",
        "dcat:endpointURL": "https://y.com/data-product/company-hr/port/2025-payroll",
        "dprod:isAccessServiceOf": {
          "@type": "dcat:Distribution",
          "dct:format": "https://www.iana.org/assignments/media-types/text/csv",
          "dprod:isDistributionOf": {
            "@id": "https://y.com/data-product/company-sales/dataset/2025-payroll",
            "@type": "dcat:Dataset",
            "rdfs:label": "Payroll",
            "dct:conformsTo": "https://y.com/schema/Payroll"
          }
        }
      }
    }
  ]
}
```

Given this example data, starting at the data product
`https://y.com/data-product/company-finance`, 
one could walk the relationships to find the input data products that feed it:

```text
https://y.com/data-product/company-finance >> 
    :inputPort >> 
    :isAccessServiceOf >> 
    :isDistributionOf >> [
        https://y.com/data-product/company-sales, 
        https://y.com/data-product/company-hr
    ]
```

In Linked Data, this would use a query such as:

```sparql
PREFIX :      <https://y.com/data-product/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dprod: <https://www.omg.org/spec/DPROD/dprod/>

SELECT DISTINCT ?input
WHERE
{ 
  :company-finance dprod:inputPort ?inputPort .
  ?inputPort dprod:isAccessServiceOf/dprod:isDistributionOf/rdfs:label ?input .
}
```

### Detailed Level: Between Datasets

To track lineage at a more granular level, 
one can also use PROV (https://www.w3.org/TR/prov-o/) at the dataset level.

```turtle
@prefix dap:     <https://data.csiro.au/dap/> .
@prefix dcat:    <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

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

See: https://www.w3.org/TR/vocab-dcat-3/#examples-dataset-provenance.
