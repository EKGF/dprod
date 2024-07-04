[ODRL](https://www.w3.org/TR/odrl-model/) is a W£C standard to describe rights and entitlements

More specifically based on ODRL, data product and dataset publishers can describe the policies, in a consistent, standard and machine-readable manner, 
and the permissions and prohibitions on specific actions that are required to be met by stakeholders.

In addition, policies maybe limited by constraints (eg. temporal or geographical constraints) and duties ( eg. payments) that may be imposed on the permissions.

Policies and their permitted or prohibited actions can be described in different levels, eg. a Policy can target a Data Product, or a Dataset or even a Data Service or a Column.

Sophisticated engines should interprete and enforce the odrl policies in the appropriate level.

```json
examplePolicyA odrl:targets exampleProduct:ProductA.
examplePolicyB odrl:targets exampleDataset:DatasetA1
```

Example of a Policy describing a permission on a specific action (distribute the data) inside a specific region:

```json
examplePolicyA odrl:permission
    [
    "action": "odrl:distribute",
    "constraint": [
       {"leftOperand": "targetCountry",
         "operator": "eq",
        "rightOperator": "region:EMEA"
    }
    ]
```
.
