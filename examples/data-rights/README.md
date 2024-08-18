[ODRL](https://www.w3.org/TR/odrl-model/) is a W3C standard to describe rights and entitlements

More specifically based on ODRL, data product and dataset publishers can describe the policies in a consistent, standard and machine-readable manner. Policies contain permissions and prohibitions on specific actions that are required to be met by stakeholders.

In addition, policies may be limited by constraints (eg. temporal or geographical constraints) and duties ( eg. payments) that may be imposed on the permissions.

Policies and their permitted or prohibited actions can be described on different levels, eg. a Policy can target a Data Product, a Dataset, a Data Service or even a Column.

Sophisticated engines should interpret and enforce the odrl policies on the appropriate level eg.:

```turtle
examplePolicyA odrl:targets exampleProduct:ProductA .
examplePolicyB odrl:targets exampleDataset:DatasetA1 .
```

An example of a Policy follows, that describes permission to distribute the data only inside a specific region:

```json
examplePolicyA odrl:permission
   {
    "action": "odrl:distribute",
    "constraint": [
       {"leftOperand": "region",
         "operator": "eq",
        "rightOperator": "region:EMEA"
       }
     ]
    }
 ```

