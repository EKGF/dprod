[ODRL](https://www.w3.org/TR/odrl-model/) is a W3C standard to describe rights and entitlements.
Based on ODRL, data product and dataset publishers can describe policies in a consistent, standard and machine-readable manner. Policies contain permissions and prohibitions on specific actions that are required to be met by stakeholders.

In addition, policies may be limited by constraints (eg. temporal or geographical constraints) and duties (eg. payments) that may be imposed on the permissions.

Policies and their permitted or prohibited actions can be described at different levels, eg. a policy can target a data product, a dataset, a data service or even a column.

Sophisticated engines should interpret and enforce the ODRL policies at the appropriate level eg.:

```turtle
examplePolicyA odrl:target exampleProduct:ProductA .
examplePolicyB odrl:target exampleDataset:DatasetA1 .
```

An example of an agreement follows, that describes permission to use all the datasets of the product if the user is working inside EMEA or APAC:

```json
examplePolicyA odrl:permission
   {
    "action": "odrl:use",
    "assignee": {
      "@type": "odrl:PartyCollection",
      "refinement": [
        {"leftOperand": "odrl:spatial",
         "operator": "odrl:isAnyOf",
         "rightOperand": ["reg:EMEA", "reg:APAC"]
        }
      ]
    }
   }
 ```

