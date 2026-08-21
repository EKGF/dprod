An Observability Port is a designated interface or endpoint in a system or 
application specifically used for monitoring and diagnostic purposes. 
It allows external tools or services to collect and analyze data related to 
the system's performance, health, and behaviour.
By exposing metrics, logs, and traces through this port, administrators and 
developers can gain insights into the system's state, troubleshoot issues, 
and ensure it operates efficiently and reliably.

## Defining Observability Ports in DPROD

DPROD has a schema-first design. 
The first thing to do is define a schema for the 
logging information. 
It could be a schema based on OpenTelemetry, but this 
uses RLOG (which is a semantic ontology for logging).

To find the Observability Port, query the ports to identify the 
ones that return an `RLOG:Entry`:

```text
outputPort >> isAccessServiceOf >> isDistributionOf >> conformsTo >> rlog:Entry
```

## Example Data Product with Observability Port

One can see that the example data product has two ports, one with the data 
and one with the logging. 
This query will return the URI of the port that returns logging 
data: `https://y.com/uk-bonds/observability-port`.

Here is an example of a data product with an observability port:

```json
{
  "@context": "https://www.omg.org/spec/DPROD/dprod-context.jsonld",
  "@graph": [
    {
      "@id": "https://y.com/data-product/uk-bonds",
      "@type": "dprod:DataProduct",
      "dprod:inputPort": [
        {
          "@id": "https://y.com/data-product/uk-bonds/port/2024-data",
          "@type": "dcat:DataService"
        }
      ],
      "dprod:outputPort": [
        {
          "@id": "https://y.com/data-product/uk-bonds/port/2024-observability",
          "@type": "dcat:DataService",
          "rdfs:label": "Observability Port",
          "dcat:endpointURL": "https://y.com/data-product/uk-bonds/port/2024-observability",
          "dprod:isAccessServiceOf": {
            "@type": "dcat:Distribution",
            "dct:format": "https://www.iana.org/assignments/media-types/application/json",
            "dprod:isDistributionOf": {
              "@id": "https://y.com/data-product/uk-bonds/dataset/2024-observability",
              "@type": "dcat:Dataset",
              "dct:conformsTo": "https://y.com/schema/ObservabilityLog"
            }
          }
        },
        {
          "@id": "https://y.com/data-product/uk-bonds/port/2024-data",
          "@type": "dcat:DataService",
          "rdfs:label": "Data Port",
          "dcat:endpointURL": "https://y.com/data-product/uk-bonds/port/2024-data",
          "dprod:isAccessServiceOf": {
            "@type": "dcat:Distribution",
            "dct:format": "https://www.iana.org/assignments/media-types/application/json",
            "dprod:isDistributionOf": {
              "@id": "https://y.com/data-product/uk-bonds/dataset/2024-data",
              "@type": "dcat:Dataset",
              "dct:conformsTo": "https://y.com/schema/Data"
            }
          }
        }
      ]
    }
  ]
}
```

Given that the schema defines the class for an observation, it can be used to 
find all observability ports on data product like this:

```text
[https://y.com/data-product/uk-bonds/port/2024-observability] >> isAccessServiceOf >> isDistributionOf >> conformsTo >> https://y.com/schema/ObservabilityLog
```

In Linked Data a SPARQL query would do that:

```sparql
SELECT ?port
WHERE
{ 
  ?port a dcat:DataService .
  ?port (dprod:isAccessServiceOf/dprod:isDistributionOf)/dcat:conformsTo rlog:Entry
}
```

This query will return the URI of the port that provides logging
data: `https://y.com/data-product/uk-bonds/port/2024-observability`.
