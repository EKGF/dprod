[ODRL](https://www.w3.org/TR/odrl-model/) is a W3C standard to describe rights and entitlements.
Based on ODRL, data product and dataset publishers can describe policies in a consistent, standard and machine-readable manner. Policies contain permissions and prohibitions on specific actions that are required to be met by stakeholders.

In addition, policies may be limited by constraints (eg. temporal or geographical constraints) and duties (eg. payments) that may be imposed on the permissions.

Policies and their permitted or prohibited actions can be described at different levels, eg. a policy can target a data product, a dataset, a data service or even a column.

Sophisticated engines should interpret and enforce the ODRL policies at the appropriate level eg.:

```turtle
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix examplePolicy: <https://data.org/policy/> .
@prefix exampleProduct: <https://data.org/data-product/> .
@prefix exampleDataset: <https://data.org/dataset/> .

examplePolicy:A odrl:target exampleProduct:ProductA .
examplePolicy:B odrl:target exampleDataset:DatasetA1 .
```

An example of an agreement follows, that describes permission to use all the datasets of the product if the user is working inside EMEA or APAC:

```json
{
  "@context": [
    "https://www.omg.org/spec/DPROD/dprod-context.jsonld",
    {
      "reg": "https://www.region.taxonomy/v/1/"
    }
  ],
  "@id": "https://data.org/policy/examplePolicyA",
  "@type": "odrl:Agreement",
  "odrl:permission": [
    {
      "odrl:target": { "@id": "https://data.org/data-product/equity-trade-xxx" },
      "odrl:action": { "@id": "odrl:use" },
      "odrl:assignee": {
        "@id": "https://example.org/DataDepartment/emea-and-apac-staff",
        "@type": "odrl:PartyCollection",
        "odrl:refinement": [
          {
            "odrl:leftOperand": { "@id": "odrl:spatial" },
            "odrl:operator": { "@id": "odrl:isAnyOf" },
            "odrl:rightOperand": [
              { "@id": "reg:EMEA" },
              { "@id": "reg:APAC" }
            ]
          }
        ]
      }
    }
  ]
}
```

