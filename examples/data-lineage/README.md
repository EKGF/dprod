## Data Lineage

It is important to be able to trace the lineage of data. Within DPROD, this can be done in two ways: at a high level from one data product to another and, if you want, at a more detailed level of the underlying datasets.

### High Level Lineage: Between Data Products

Data products have input and output ports, and one data product’s input port will point to another data product’s output port.

This allows a user to query the lineage. The data products all have URLs as identifiers, and properties all connect to each other, so you can walk from one data product to the downstream data products that feed it.

You can follow the path that leads from one data product to another like this:

```text
Data Product >> inputPort >> isAccessServiceOf >> isDistributionOf >> Input Data Product 
```

Let's look at some example data with three data products that connect to each other through their input and output ports: 
```json
{
  "@context": "https://ekgf.github.io/dprod/dprod.jsonld",
  "dataProducts": [
    {
      "id": "https://y.com/data-product/company-finance",
      "type": "DataProduct",
      "inputPort": [
        {
          "id": "https://y.com/data-product/company-sales/port/2025-sales",
          "type": "DataService"
        },
        {
          "id": "https://y.com/data-product/company-hr/port/2025-payroll",
          "type": "DataService"
        }
      ],
      "outputPort": {
        "id": "https://y.com/data-product/company-sales/port/2025-balance-sheet",
        "type": "DataService",
        "label": "Balance Sheet",
        "endpointURL": "https://y.com/data-product/company-sales/port/2025-c",
        "isAccessServiceOf": {
          "type": "Distribution",
          "format": "https://www.iana.org/assignments/media-types/application/json",
          "isDistributionOf": {
            "type": "Dataset",
            "id": "https://y.com/data-product/company-sales/dataset/2025-balance-sheet",
            "conformsTo": "https://y.com/schema/BalanceSheet"
          }
        }
      }
    },
    {
      "id": "https://y.com/data-product/company-sales",
      "type": "DataProduct",
      "outputPort": {
        "id": "https://y.com/data-product/company-sales/port/2025-sales",
        "type": "DataService",
        "label": "Sales",
        "endpointURL": "https://y.com/data-product/company-sales/port/2025-sales",
        "isAccessServiceOf": {
          "type": "Distribution",
          "format": "https://www.iana.org/assignments/media-types/application/json",
          "isDistributionOf": {
            "type": "Dataset",
            "label": "Sales",
            "id": "https://y.com/data-product/company-sales/dataset/2025-sales",
            "conformsTo": "https://y.com/schema/Sale"
          }
        }
      }
    },
    {
      "id": "https://y.com/data-product/company-hr",
      "type": "DataProduct",
      "outputPort": {
        "id": "https://y.com/data-product/company-sales/port/2025-payroll",
        "type": "DataService",
        "label": "Payroll",
        "endpointURL": "https://y.com/data-product/company-hr/port/2025-payroll",
        "isAccessServiceOf": {
          "type": "Distribution",
          "format": "https://www.iana.org/assignments/media-types/text/csv",
          "isDistributionOf": {
            "type": "Dataset",
            "label": "Payroll",
            "id": "https://y.com/data-product/company-sales/dataset/2025-payroll",
            "conformsTo": "https://y.com/schema/Payroll"
          }
        }
      }
    }
  ]
}
```

Given this example data, if we started at the data product `https://y.com/data-product/company-finance`, we could walk the relationships to find the input data products that feed it:
```text
https://y.com/data-product/company-finance >> :inputPort >> :isAccessServiceOf >> :isDistributionOf >> [https://y.com/data-product/company-sales , https://y.com/data-product/company-hr]
```

In Linked Data, we would actually do this with a query like this:
```sparql
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dprod: <https://ekgf.github.io/dprod/#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <https://y.com/data-product/>

SELECT DISTINCT ?input
WHERE
{ 
  :company-finance dprod:inputPort ?inputPort.
  ?inputPort dprod:isAccessServiceOf/dprod:isDistributionOf/rdfs:label ?input.
}
```



### Detailed Level: Between Datasets

If you wish to track lineage at a more granular level, you can also use PROV (https://www.w3.org/TR/prov-o/) at the dataset level.

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

See: https://www.w3.org/TR/vocab-dcat-3/#examples-dataset-provenance.
