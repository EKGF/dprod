It is important to be able to trace the lineage of data. Data Products have input and output ports, and one Data Product’s input port will point to another Data Product’s output port.

This allows a user to query the lineage of where the data has come from by following the inputs. Here is an example query that will return all the input datasets for the finance data product.

```sparql
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dprod: <https://ekgf.github.io/data-product-spec/dprod/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <https://y.com/data-product/>

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

NOTE: If you wish to track lineage at a more granular level, you can also use PROV (https://www.w3.org/TR/prov-o/) at the dataset level. See: https://www.w3.org/TR/vocab-dcat-3/#examples-dataset-provenance.
