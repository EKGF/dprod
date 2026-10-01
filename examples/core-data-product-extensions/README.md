For real world data products, the core data product details will be part of a 
wider set of metadata that allows the data and data product to be used effectively. 

Below is an example of extending the DPROD data product, 
specifically by adding an agreement to a data product.

In this example, a Data Product Agreement is defined as a subclass of FIBO Agreement. 

*Definition of a simple Agreement based on FIBO:*

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
    {
      "fibo": "http://spec.edmcouncil.org/fibo/ontology/FND/Agreements/MetadataFNDAgreements/#",
      "ex": "http://example.org/dp#"
    }
  ],
  "@graph": [
    {
      "id": "ex:isSubjectToAgreement",
      "type": "rdf:Property",
      "label": "Data Product is Subject To FIBO Agreement",
      "rdfs:domain": { "id": "dprod:DataProduct" },
      "rdfs:range": { "id": "ex:DataProductAgreement" }
    },
    {
      "id": "ex:DataProductAgreement",
      "type": "rdfs:Class",
      "label": "DataProductAgreement",
      "rdfs:subClassOf": { "id": "fibo:Agreement" }
    }
  ]
}
```

A full definition of agreements for data products is likely to be more complex 
than a single class and may use other information models or their profiles 
(such as ODRL Policy) or create dedicated definitions.

Below is an example of a Data Product with an associated Data Product Agreement with an effective date.

*Using the agreement:*

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
    {
      "fibo": "http://spec.edmcouncil.org/fibo/ontology/FND/Agreements/MetadataFNDAgreements/#",
      "ex": "http://example.org/dp#"
    }
  ],
  "@graph": [
    {
      "id": "https://y.com/data-product/company-sales",
      "type": "DataProduct",
      "outputPort": {
        "id": "https://y.com/data-product/company-sales/port/2025-sales",
        "type": "DataService",
        "label": "Sales",
        "endpointURL": "https://y.com/data-product/company-sales/port/2025-sales",
        "isAccessServiceOf": {
          "id": "https://y.com/data-product/company-sales/distribution/2025-sales",
          "type": "Distribution",
          "format": "https://www.iana.org/assignments/media-types/application/json",
          "isDistributionOf": {
            "id": "https://y.com/data-product/company-sales/dataset/2025-sales",
            "type": "Dataset",
            "label": "Sales",
            "conformsTo": "https://y.com/schema/Sale"
          }
        }
      },
      "ex:isSubjectToAgreement": { "id": "ex:VVSimpleAgreement" }
    },
    {
      "id": "ex:VVSimpleAgreement",
      "type": "ex:DataProductAgreement",
      "label": "Very Simple Data Product Agreement",
      "fibo:hasEffectiveDate": { "type": "xsd:date", "@value": "2024-08-31" }
    }
  ]
}
```
